from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import os
import sys
import re
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

# Global variables for loaded data
model = None
index = None
article_ids = None
articles_data = None

# OpenAI API configuration
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def is_pure_english(text):
    """Check if text contains only English characters, numbers, and common punctuation"""
    # Allow English letters, numbers, spaces, and common punctuation
    english_pattern = r'^[a-zA-Z0-9\s\.,;:!?\-\(\)\[\]\{\}\'\"/\\@#$%^&*+=<>~`|]+$'
    return bool(re.match(english_pattern, text))

def translate_with_chatgpt(query):
    """Translate query using ChatGPT API with cheaper model"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use cheaper model instead of gpt-4o
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical translator. Translate medical queries to English. Keep English terms unchanged, only translate non-English parts. Return only the translated text without explanation."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            max_tokens=100,
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return query  # Return original query if translation fails

def expand_query_with_gpt(query):
    """Expand the user query into a set of more specific, academic terms using GPT."""
    try:
        prompt = f"""You are a biomedical research query analyst. Your task is to expand a user's query into a set of 3 to 5 semantically related, specific search terms that are likely to appear in PubMed abstracts. Focus on academic and technical vocabulary.

Return the result as a JSON array of strings. Only return the JSON array, nothing else.

User Query: "{query}"
"""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides expanded search terms in a JSON array format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        # The model might return a dictionary with a key, e.g., {"queries": [...]}. We need to find the list.
        for value in result.values():
            if isinstance(value, list):
                print(f"Expanded query to: {value}")
                return value
        
        # If no list is found, return the original query
        return [query]

    except Exception as e:
        print(f"Query expansion error: {str(e)}")
        return [query] # Return original query in a list if expansion fails

def build_context_from_articles(articles, max_length=4000):
    """Build context string from retrieved articles"""
    context_parts = []
    current_length = 0
    
    for article in articles:
        # Format article information
        article_text = f"PMID: {article['pmid']}\n"
        article_text += f"Title: {article['title']}\n"
        article_text += f"Journal: {article['journal']}\n"
        article_text += f"Publication Date: {article['pub_date']}\n"
        article_text += f"Abstract: {article['abstract']}\n"
        article_text += f"Authors: {', '.join(article['authors'])}\n"
        article_text += "-" * 50 + "\n"
        
        # Check if adding this article would exceed max length
        if current_length + len(article_text) > max_length:
            break
            
        context_parts.append(article_text)
        current_length += len(article_text)
    
    return "\n".join(context_parts)

def generate_rag_answer(question, context, original_question):
    """Generate answer using RAG approach"""
    try:
        # Detect if the question is about a specific region by checking the translated question
        is_taiwan_question = any(keyword in question.lower() for keyword in ['taiwan', 'taiwanese'])
        is_china_question = any(keyword in question.lower() for keyword in ['china', 'chinese'])
        is_korea_question = any(keyword in question.lower() for keyword in ['korea', 'korean'])
        
        # Build region-specific instructions
        region_instruction = ""
        if is_taiwan_question:
            region_instruction = "Focus specifically on Taiwan and the Taiwanese healthcare system. Prioritize Taiwan-specific information. If the provided literature is about other regions (e.g., China), first state that the documents are not about Taiwan, and then you may draw cautious parallels if relevant, but clearly label it as a comparison. Explicitly state if no direct information on Taiwan is found."
        elif is_china_question:
            region_instruction = "Focus specifically on China and the Chinese healthcare system. Prioritize China-specific information."
        elif is_korea_question:
            region_instruction = "Focus specifically on Korea and the Korean healthcare system. Prioritize Korea-specific information."
        else:
            region_instruction = "Provide a balanced analysis based on the available literature."
        
        prompt = f"""You are a medical research assistant specialized in helping with PubMed medical literature research.

YOUR ROLE AND CAPABILITIES:
- You can answer questions about medical research, healthcare systems, diseases, treatments, and health policy based on PubMed literature.
- You CANNOT provide personal medical advice, diagnosis, or treatment recommendations.

Question: {original_question}

Relevant Medical Literature:
{context}

Instructions:
1.  Answer based *only* on the provided "Relevant Medical Literature". Do not use outside knowledge.
2.  {region_instruction}
3.  Provide a comprehensive answer that includes key findings, methodologies, and conclusions from the literature.
4.  When citing studies, use proper APA format: (First Author et al., Year; PMID: XXXX).
5.  Extract the year from the 'pub_date' field for citations.
6.  If the literature does not contain enough information to answer the question, clearly state this limitation.
7.  Answer in the same language as the original user question (`{original_question}`).
8.  Structure your answer logically with clear sections if appropriate.

Answer:"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical research assistant. You help with PubMed literature research by answering questions based *only* on the provided literature. You must adhere to the user's instructions, especially regarding region-specific focus and citation format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1500,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"RAG answer generation error: {str(e)}")
        return f"Sorry, I encountered an error while generating the answer: {str(e)}"

def load_data():
    """Load FAISS index and article data"""
    global model, index, article_ids, articles_data
    
    print("Loading FAISS index and data...")
    
    # Load the sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Load FAISS index
    index_path = "../../output/embeddings/faiss.index"
    index = faiss.read_index(index_path)
    
    # Load article IDs
    with open("../../output/embeddings/article_ids.json", 'r', encoding='utf-8') as f:
        article_ids = json.load(f)
    
    # Load articles data
    with open("../../output/cleaned_data/cleaned_articles.json", 'r', encoding='utf-8') as f:
        articles_data = json.load(f)
    
    print(f"Loaded {len(article_ids)} articles and FAISS index")

@app.route('/api/search', methods=['POST'])
def search():
    """Search articles using semantic similarity with translation support"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 10)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        original_query = query
        translated_query = query
        
        # Check if query contains Chinese characters
        if not is_pure_english(query):
            print(f"Original query (contains non-English characters): {query}")
            translated_query = translate_with_chatgpt(query)
            print(f"Translated query: {translated_query}")
        
        # Encode the query (use translated version if available)
        query_embedding = model.encode([translated_query])
        
        # Search in FAISS index
        distances, indices = index.search(query_embedding, top_k)
        
        # Get results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(article_ids):
                pmid = article_ids[idx]
                
                # Find article data
                article = None
                for art in articles_data:
                    if art.get('pmid') == pmid:
                        article = art
                        break
                
                if article:
                    results.append({
                        'rank': i + 1,
                        'pmid': pmid,
                        'title': article.get('title', ''),
                        'abstract': article.get('abstract', ''),
                        'journal': article.get('journal', ''),
                        'pub_date': article.get('pub_date', ''),
                        'authors': article.get('authors', []),
                        'similarity_score': float(1 - distance)  # Convert distance to similarity
                    })
        
        return jsonify({
            'original_query': original_query,
            'translated_query': translated_query,
            'total_results': len(results),
            'results': results
        })
        
    except Exception as e:
        print(f"Error in search: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search_with_progress', methods=['POST'])
def search_with_progress():
    """Search articles with real-time progress updates"""
    # Get request data outside of the generator
    data = request.get_json()
    query = data.get('query', '')
    top_k = data.get('top_k', 10)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    def generate():
        try:
            original_query = query
            translated_query = query
            
            # Step 1: Check for Chinese characters
            yield f"data: {json.dumps({'step': 'Detecting non-English characters in query...', 'progress': 10})}\n\n"
            time.sleep(0.5)  # Small delay for visual effect
            
            # Step 2: Translate if needed
            if not is_pure_english(query):
                yield f"data: {json.dumps({'step': 'Translating query to English...', 'progress': 20, 'translation_info': f'Original: {original_query}'})}\n\n"
                print(f"Original query (contains non-English characters): {query}")
                translated_query = translate_with_chatgpt(query)
                print(f"Translated query: {translated_query}")
                yield f"data: {json.dumps({'step': 'Translation completed', 'progress': 25, 'translation_result': f'Translated: {translated_query}'})}\n\n"
                time.sleep(0.5)
            else:
                yield f"data: {json.dumps({'step': 'Query is in English, skipping translation', 'progress': 25})}\n\n"
                time.sleep(0.5)
            
            # Step 3: Generate embedding
            yield f"data: {json.dumps({'step': 'Generating query embedding...', 'progress': 40})}\n\n"
            query_embedding = model.encode([translated_query])
            time.sleep(0.5)
            
            # Step 4: Search in FAISS
            yield f"data: {json.dumps({'step': 'Searching in vector database...', 'progress': 60})}\n\n"
            distances, indices = index.search(query_embedding, top_k)
            time.sleep(0.5)
            
            # Step 5: Retrieve article details
            yield f"data: {json.dumps({'step': 'Retrieving article details...', 'progress': 80})}\n\n"
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(article_ids):
                    pmid = article_ids[idx]
                    
                    # Find article data
                    article = None
                    for art in articles_data:
                        if art.get('pmid') == pmid:
                            article = art
                            break
                    
                    if article:
                        results.append({
                            'rank': i + 1,
                            'pmid': pmid,
                            'title': article.get('title', ''),
                            'abstract': article.get('abstract', ''),
                            'journal': article.get('journal', ''),
                            'pub_date': article.get('pub_date', ''),
                            'authors': article.get('authors', []),
                            'similarity_score': float(1 - distance)
                        })
            
            # Step 6: Complete
            yield f"data: {json.dumps({'step': 'Search completed!', 'progress': 100})}\n\n"
            time.sleep(0.5)
            
            # Final result
            yield f"data: {json.dumps({'complete': True, 'original_query': original_query, 'translated_query': translated_query, 'total_results': len(results), 'results': results})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

@app.route('/api/rag_qa_with_progress', methods=['POST'])
def rag_qa_with_progress():
    """RAG-based question answering with real-time progress updates"""
    # Get request data outside of the generator
    data = request.get_json()
    question = data.get('question', '')
    top_k = data.get('top_k', 12)  # Increased from 8 to 12 for more comprehensive answers
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    def generate():
        try:
            original_question = question
            translated_question = question
            
            # Step 1: Check for Chinese characters
            yield f"data: {json.dumps({'step': 'Detecting non-English characters in question...', 'progress': 10})}\n\n"
            time.sleep(0.5)
            
            # Step 2: Translate if needed
            if not is_pure_english(question):
                yield f"data: {json.dumps({'step': 'Translating question to English...', 'progress': 20, 'translation_info': f'Original: {original_question}'})}\n\n"
                print(f"Original question (contains non-English characters): {question}")
                translated_question = translate_with_chatgpt(question)
                print(f"Translated question: {translated_question}")
                yield f"data: {json.dumps({'step': 'Translation completed', 'progress': 25, 'translation_result': f'Translated: {translated_question}'})}\n\n"
                time.sleep(0.5)
            else:
                yield f"data: {json.dumps({'step': 'Question is in English, skipping translation', 'progress': 25})}\n\n"
                time.sleep(0.5)
            
            # New Step: Query Expansion
            yield f"data: {json.dumps({'step': 'Expanding query for better search...', 'progress': 30})}\n\n"
            expanded_queries = expand_query_with_gpt(translated_question)
            all_queries_for_embedding = [translated_question] + expanded_queries
            time.sleep(0.5)
            
            # Step 3: Generate embedding (now using multiple queries)
            yield f"data: {json.dumps({'step': 'Generating query embeddings...', 'progress': 40})}\n\n"
            embeddings = model.encode(all_queries_for_embedding)
            # Average the embeddings to create a single, more robust query vector
            avg_embedding = np.mean(embeddings, axis=0, keepdims=True)
            time.sleep(0.5)
            
            # Step 4: Search for relevant articles
            yield f"data: {json.dumps({'step': 'Searching for relevant articles...', 'progress': 50})}\n\n"
            distances, indices = index.search(avg_embedding, top_k)
            time.sleep(0.5)
            
            # Step 5: Retrieve article details
            yield f"data: {json.dumps({'step': 'Retrieving article details...', 'progress': 70})}\n\n"
            relevant_articles = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(article_ids):
                    pmid = article_ids[idx]
                    
                    # Find article data
                    article = None
                    for art in articles_data:
                        if art.get('pmid') == pmid:
                            article = art
                            break
                    
                    if article:
                        relevant_articles.append({
                            'rank': i + 1,
                            'pmid': pmid,
                            'title': article.get('title', ''),
                            'abstract': article.get('abstract', ''),
                            'journal': article.get('journal', ''),
                            'pub_date': article.get('pub_date', ''),
                            'authors': article.get('authors', []),
                            'similarity_score': float(1 - distance)
                        })
            
            # Step 6: Build context
            yield f"data: {json.dumps({'step': 'Building context from articles...', 'progress': 80})}\n\n"
            context = build_context_from_articles(relevant_articles)
            time.sleep(0.5)
            
            # Step 7: Generate AI answer
            yield f"data: {json.dumps({'step': 'Generating AI answer...', 'progress': 90})}\n\n"
            answer = generate_rag_answer(translated_question, context, original_question)
            time.sleep(0.5)
            
            # Step 8: Complete
            yield f"data: {json.dumps({'step': 'RAG analysis completed!', 'progress': 100})}\n\n"
            time.sleep(0.5)
            
            # Final result
            yield f"data: {json.dumps({'complete': True, 'original_question': original_question, 'translated_question': translated_question, 'answer': answer, 'relevant_articles': relevant_articles, 'articles_used': len(relevant_articles)})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

@app.route('/api/rag_qa', methods=['POST'])
def rag_question_answer():
    """RAG-based question answering system"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        top_k = data.get('top_k', 12)  # Default to 12 articles for RAG (increased from 8)
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        original_question = question
        translated_question = question
        
        # Check if question contains Chinese characters
        if not is_pure_english(question):
            print(f"Original question (contains non-English characters): {question}")
            translated_question = translate_with_chatgpt(question)
            print(f"Translated question: {translated_question}")
        
        # Encode the question (use translated version if available)
        question_embedding = model.encode([translated_question])
        
        # Search in FAISS index
        distances, indices = index.search(question_embedding, top_k)
        
        # Get relevant articles
        relevant_articles = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(article_ids):
                pmid = article_ids[idx]
                
                # Find article data
                article = None
                for art in articles_data:
                    if art.get('pmid') == pmid:
                        article = art
                        break
                
                if article:
                    relevant_articles.append({
                        'rank': i + 1,
                        'pmid': pmid,
                        'title': article.get('title', ''),
                        'abstract': article.get('abstract', ''),
                        'journal': article.get('journal', ''),
                        'pub_date': article.get('pub_date', ''),
                        'authors': article.get('authors', []),
                        'similarity_score': float(1 - distance)
                    })
        
        # Build context from relevant articles
        context = build_context_from_articles(relevant_articles)
        
        # Generate answer using RAG
        answer = generate_rag_answer(translated_question, context, original_question)
        
        return jsonify({
            'original_question': original_question,
            'translated_question': translated_question,
            'answer': answer,
            'relevant_articles': relevant_articles,
            'articles_used': len(relevant_articles)
        })
        
    except Exception as e:
        print(f"Error in RAG QA: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate():
    """Translate query using ChatGPT"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        if not is_pure_english(query):
            translated = translate_with_chatgpt(query)
            return jsonify({
                'original': query,
                'translated': translated,
                'is_pure_english': False
            })
        else:
            return jsonify({
                'original': query,
                'translated': query,
                'is_pure_english': True
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        return jsonify({
            'total_articles': len(article_ids),
            'index_size': index.ntotal if index else 0,
            'model_name': 'all-MiniLM-L6-v2',
            'translation_support': True,
            'rag_support': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'PubMed Search API with Translation and RAG is running'})

if __name__ == '__main__':
    # Load data on startup
    load_data()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000) 