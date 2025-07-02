import re
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API configuration
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def is_pure_english(text):
    """Check if text contains only English characters, numbers, and common punctuation"""
    # Allow English letters, numbers, spaces, and common punctuation
    english_pattern = r'^[a-zA-Z0-9\s\.,;:!?\-\(\)\[\]\{\}\'\"/\\@#$%^&*+=<>~`|]+$'
    return bool(re.match(english_pattern, text))

def translate_with_chatgpt(query):
    """
    Analyzes the source query to determine its language and translates it to English.
    Returns a dictionary containing the translated text and the source language.
    """
    try:
        prompt = f"""You are a language analysis and translation expert. Your task is to analyze the following text.
1. Identify the source language. Distinguish between "English", "Simplified Chinese", and "Traditional Chinese". For other languages, identify them by name (e.g., "Japanese").
2. Translate the text to English.

Return a single JSON object with two keys: "source_language" and "translated_text".

User Text: "{query}"
"""
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that analyzes and translates text, returning the result in a specific JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        print(f"Language analysis result: {result}")
        return {
            'translated_text': result.get('translated_text', query),
            'source_language': result.get('source_language', 'English')
        }

    except Exception as e:
        print(f"Translation and language analysis error: {str(e)}")
        # Fallback in case of error
        return {
            'translated_text': query,
            'source_language': 'English'
        }

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

def build_context_from_articles(articles, max_length=12000):
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
        article_text += f"Authors: {', '.join(article['authors']) if isinstance(article.get('authors'), list) else article.get('authors', '')}\n"
        article_text += "-" * 50 + "\n"
        
        # Check if adding this article would exceed max length
        if current_length + len(article_text) > max_length:
            break
            
        context_parts.append(article_text)
        current_length += len(article_text)
    
    print(f"Selected {len(context_parts)}/{len(articles)} articles for context. (max_length: {max_length}, actual_length: {current_length})")
    return "\n".join(context_parts)

def should_trigger_low_similarity_response(relevant_articles):
    """Check if we should trigger low similarity response"""
    if not relevant_articles or len(relevant_articles) == 0:
        return True, "No articles found"
    
    # Check if any article has similarity > 30%
    max_similarity = max(article.get('similarity_score', 0) for article in relevant_articles)
    if max_similarity < 0.3:
        return True, f"Maximum similarity ({max_similarity:.1%}) below 30% threshold"
    
    # Check if too few articles
    if len(relevant_articles) <= 3:
        return True, f"Only {len(relevant_articles)} articles found"
    
    return False, None

def generate_no_relevant_literature_response(original_question, source_language):
    """Generate response when no relevant literature is found"""
    return f"""
I apologize, but I cannot find any literature directly relevant to your question "{original_question}" in the current medical literature database.

**Possible reasons:**
- Your question may involve a newer research area
- The database may lack literature on this specific topic
- Query terms may need adjustment

**Suggestions:**
- Try rephrasing your question with different keywords
- Consider asking about related but broader concepts
- Or ask a more general related question

If needed, I can help you reformulate your query for better results.
"""

def generate_low_relevance_response(original_question, source_language, max_similarity, article_count):
    """Generate response when articles have low relevance"""
    return f"""
I found {article_count} articles in the database, but none have high relevance to your question "{original_question}". The most relevant article has only {max_similarity:.1%} similarity.

**Analysis:**
- Found {article_count} articles with limited relevance
- Maximum similarity: {max_similarity:.1%}
- This suggests the topic may not be well-covered in our current database

**Suggestions:**
- Try using different keywords or broader terms
- Consider asking about related topics
- The available literature may not address your specific question

Would you like me to provide a brief analysis of the available articles, or would you prefer to rephrase your question?
"""

def generate_limited_articles_response(original_question, source_language, article_count, avg_similarity):
    """Generate response when few articles are found but they have good relevance"""
    return f"""
I found only {article_count} articles relevant to your question "{original_question}" in the database. While these articles have good relevance (average similarity: {avg_similarity:.1%}), the limited number may not provide a comprehensive answer.

**Note:**
- Only {article_count} articles found
- Average similarity: {avg_similarity:.1%}
- Limited sample size may affect answer completeness

**Suggestions:**
- Consider asking a broader question to get more results
- The available literature may be sufficient for basic information
- You may want to explore related topics for more comprehensive coverage

I'll provide an analysis based on the available articles, but please note the limited scope.
"""

def generate_normal_rag_response(question, context, original_question, source_language):
    """Generate normal RAG response when conditions are good"""
    import os
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    try:
        context_article_count = context.count("PMID:")
        print(f"Generating RAG answer using {context_article_count} articles in context.")

        is_taiwan_question = any(keyword in question.lower() for keyword in ['taiwan', 'taiwanese'])
        is_china_question = any(keyword in question.lower() for keyword in ['china', 'chinese'])

        region_instruction = ""
        if is_taiwan_question:
            region_instruction = "Focus specifically on Taiwan and the Taiwanese healthcare system. Prioritize Taiwan-specific information. If the provided literature is about other regions (e.g., China), first state that the documents are not about Taiwan, and then you may draw cautious parallels if relevant, but clearly label it as a comparison. Explicitly state if no direct information on Taiwan is found."
        elif is_china_question:
            region_instruction = "Focus specifically on China and the Chinese healthcare system. Prioritize China-specific information."
        else:
            region_instruction = "Provide a balanced analysis based on the available literature."

        language_instruction = f"Answer in the same language as the original user question ({source_language})."
        if source_language == "Traditional Chinese":
            language_instruction = "The user asked in Traditional Chinese. Your entire response MUST be in Traditional Chinese (繁體中文)."
        elif source_language == "Simplified Chinese":
            language_instruction = "The user asked in Simplified Chinese. Your entire response MUST be in Simplified Chinese (简体中文)."
        
        prompt = f"""You are a medical research assistant specialized in helping with PubMed medical literature research.

YOUR ROLE AND CAPABILITIES:
- You can answer questions about medical research, healthcare systems, diseases, treatments, and health policy based on PubMed literature.
- You CANNOT provide personal medical advice, diagnosis, or treatment recommendations.

Question: {original_question}

Relevant Medical Literature (Based on {context_article_count} articles):
{context}

Instructions:
1.  Answer based *only* on the provided "Relevant Medical Literature". Do not use outside knowledge.
2.  {region_instruction}
3.  Provide a comprehensive answer that includes key findings, methodologies, and conclusions from the literature.
4.  When citing studies, use proper APA format: (First Author et al., Year; PMID: XXXX).
5.  Extract the year from the 'pub_date' field for citations.
6.  If the literature does not contain enough information to answer the question, clearly state this limitation.
7.  {language_instruction}
8.  Answer in the same language as the original user question (`{original_question}`).
9.  Structure your answer logically with clear sections if appropriate.

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
        # Re-raise the exception to be caught by the main generator's handler
        raise e

def generate_rag_answer(question, context, original_question, source_language, relevant_articles=None):
    """Generate answer using RAG approach with improved similarity checking"""
    
    # Check if we should trigger special responses
    should_trigger, reason = should_trigger_low_similarity_response(relevant_articles)
    
    if should_trigger:
        if not relevant_articles or len(relevant_articles) == 0:
            print(f"Triggering no relevant literature response: {reason}")
            return generate_no_relevant_literature_response(original_question, source_language)
        
        max_similarity = max(article.get('similarity_score', 0) for article in relevant_articles)
        article_count = len(relevant_articles)
        
        if max_similarity < 0.3:
            if article_count <= 3:
                print(f"Triggering no relevant literature response: {reason}")
                return generate_no_relevant_literature_response(original_question, source_language)
            else:
                print(f"Triggering low relevance response: {reason}")
                return generate_low_relevance_response(original_question, source_language, max_similarity, article_count)
        elif article_count <= 3:
            avg_similarity = sum(article.get('similarity_score', 0) for article in relevant_articles) / article_count
            print(f"Triggering limited articles response: {reason}")
            return generate_limited_articles_response(original_question, source_language, article_count, avg_similarity)
    
    # Normal response for good similarity and sufficient articles
    print("Generating normal RAG response")
    return generate_normal_rag_response(question, context, original_question, source_language) 