import json
import time
import numpy as np
from flask import request, jsonify, Response, current_app, stream_with_context
from . import api_bp
from utils.helpers import is_pure_english, translate_with_chatgpt, expand_query_with_gpt, build_context_from_articles, generate_rag_answer

@api_bp.route('/search', methods=['POST'])
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
            translation_result = translate_with_chatgpt(query)
            translated_query = translation_result['translated_text']
            print(f"Translated query: {translated_query}")
        
        # Encode the query (use translated version if available)
        query_embedding = current_app.model.encode([translated_query])
        
        # Search in FAISS index
        distances, indices = current_app.index.search(query_embedding, top_k)
        
        # Get results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(current_app.article_ids):
                pmid = str(current_app.article_ids[idx])
                
                # O(1) lookup instead of O(N) loop
                article = current_app.articles_data_dict.get(pmid)
                
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

@api_bp.route('/search_with_progress', methods=['POST'])
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
            
            # Step 1: Check for non-English characters
            yield f"data: {json.dumps({'step': 'detect'})}\n\n"
            time.sleep(0.5)  # Small delay for visual effect
            
            # Step 2: Translate if needed
            if not is_pure_english(query):
                yield f"data: {json.dumps({'step': 'translate', 'translation_info': f'Original: {original_query}'})}\n\n"
                print(f"Original query (contains non-English characters): {query}")
                translation_result = translate_with_chatgpt(query)
                translated_query = translation_result['translated_text']
                print(f"Translated query: {translated_query}")
                yield f"data: {json.dumps({'step': 'translate', 'translation_result': f'Translated: {translated_query}'})}\n\n"
                time.sleep(0.5)
            else:
                yield f"data: {json.dumps({'step': 'translate'})}\n\n"
                time.sleep(0.5)
            
            # Step 3: Generate embedding
            yield f"data: {json.dumps({'step': 'embedding'})}\n\n"
            query_embedding = current_app.model.encode([translated_query])
            time.sleep(0.5)
            
            # Step 4: Search in FAISS
            yield f"data: {json.dumps({'step': 'search'})}\n\n"
            distances, indices = current_app.index.search(query_embedding, top_k)
            time.sleep(0.5)
            
            # Step 5: Retrieve article details
            yield f"data: {json.dumps({'step': 'retrieve'})}\n\n"
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(current_app.article_ids):
                    pmid = str(current_app.article_ids[idx])
                    
                    # O(1) lookup instead of O(N) loop
                    article = current_app.articles_data_dict.get(pmid)
                    
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
            yield f"data: {json.dumps({'step': 'complete'})}\n\n"
            time.sleep(0.5)
            
            # Final result
            yield f"data: {json.dumps({'complete': True, 'original_query': original_query, 'translated_query': translated_query, 'total_results': len(results), 'results': results})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/plain')

@api_bp.route('/rag_qa_with_progress', methods=['POST'])
def rag_qa_with_progress():
    """RAG-based question answering with real-time progress updates"""
    data = request.get_json()
    question = data.get('question', '')
    top_k = data.get('top_k', 20)

    if not question:
        return jsonify({'error': 'Question is required'}), 400

    def generate():
        try:
            original_question = question
            translated_question = question
            source_language = 'English'
            
            # Step 1: Language Analysis
            yield f"data: {json.dumps({'step': 'detect'})}\n\n"
            time.sleep(0.5)
            
            # Step 2: Translation
            if not is_pure_english(question):
                yield f"data: {json.dumps({'step': 'translate', 'translation_info': f'Original: {original_question}'})}\n\n"
                translation_result = translate_with_chatgpt(question)
                translated_question = translation_result['translated_text']
                source_language = translation_result['source_language']
                
                yield f"data: {json.dumps({'step': 'translate', 'translation_result': f'Translated: {translated_question}'})}\n\n"
                time.sleep(0.5)
            else:
                yield f"data: {json.dumps({'step': 'translate'})}\n\n"
                time.sleep(0.5)

            # Step 3: Query Expansion
            yield f"data: {json.dumps({'step': 'expand'})}\n\n"
            expanded_queries = expand_query_with_gpt(translated_question)
            all_queries_for_embedding = [translated_question] + expanded_queries
            time.sleep(0.5)
            
            # Step 4: Generate embedding (now using multiple queries)
            yield f"data: {json.dumps({'step': 'embedding'})}\n\n"
            embeddings = current_app.model.encode(all_queries_for_embedding)
            # Average the embeddings to create a single, more robust query vector
            avg_embedding = np.mean(embeddings, axis=0, keepdims=True)
            time.sleep(0.5)
            
            # Step 5: Search for relevant articles
            yield f"data: {json.dumps({'step': 'search'})}\n\n"
            distances, indices = current_app.index.search(avg_embedding, top_k)
            time.sleep(0.5)
            
            # Step 6: Retrieve article details
            yield f"data: {json.dumps({'step': 'retrieve'})}\n\n"
            relevant_articles = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(current_app.article_ids):
                    pmid = str(current_app.article_ids[idx])
                    
                    # O(1) lookup instead of O(N) loop
                    article = current_app.articles_data_dict.get(pmid)
                    
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
            
            # Step 7: Build context
            yield f"data: {json.dumps({'step': 'context'})}\n\n"
            context = build_context_from_articles(relevant_articles)
            time.sleep(0.5)
            
            # Step 8: Generate AI answer
            yield f"data: {json.dumps({'step': 'generate'})}\n\n"
            answer = generate_rag_answer(translated_question, context, original_question, source_language)
            time.sleep(0.5)
            
            # Step 9: Complete
            yield f"data: {json.dumps({'step': 'complete'})}\n\n"
            time.sleep(0.5)
            
            # Final result
            yield f"data: {json.dumps({'complete': True, 'original_question': original_question, 'translated_question': translated_question, 'answer': answer, 'relevant_articles': relevant_articles, 'articles_used': len(relevant_articles)})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/plain')

@api_bp.route('/rag_qa', methods=['POST'])
def rag_question_answer():
    """RAG-based question answering system"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        top_k = data.get('top_k', 20)  # Default to 20 articles for RAG (increased from 12)
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        original_question = question
        translated_question = question
        
        # Check if question contains Chinese characters
        if not is_pure_english(question):
            print(f"Original question (contains non-English characters): {question}")
            translation_result = translate_with_chatgpt(question)
            translated_question = translation_result['translated_text']
            print(f"Translated question: {translated_question}")
        
        # Encode the question (use translated version if available)
        question_embedding = current_app.model.encode([translated_question])
        
        # Search in FAISS index
        distances, indices = current_app.index.search(question_embedding, top_k)
        
        # Get relevant articles
        relevant_articles = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(current_app.article_ids):
                pmid = str(current_app.article_ids[idx])
                
                # O(1) lookup instead of O(N) loop
                article = current_app.articles_data_dict.get(pmid)
                
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
        answer = generate_rag_answer(translated_question, context, original_question, 'English')
        
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

@api_bp.route('/translate', methods=['POST'])
def translate():
    """Translate query using ChatGPT"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        if not is_pure_english(query):
            translation_result = translate_with_chatgpt(query)
            return jsonify({
                'original': query,
                'translated': translation_result['translated_text'],
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

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        return jsonify({
            'total_articles': len(current_app.article_ids),
            'index_size': current_app.index.ntotal if current_app.index else 0,
            'model_name': 'all-MiniLM-L6-v2',
            'translation_support': True,
            'rag_support': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'PubMed Search API with Translation and RAG is running'}) 