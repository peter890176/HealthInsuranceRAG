#!/usr/bin/env python3
"""
Regenerate FAISS index with current FAISS version to ensure compatibility
"""

import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def remove_old_files():
    """Remove old index and related files"""
    files_to_remove = ['pubmed_faiss.index', 'article_ids.json']
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            logger.info(f"Removed old file: {file}")
        else:
            logger.info(f"File not found (already removed): {file}")

def load_articles():
    """Load articles data"""
    logger.info("Loading articles data...")
    with open('pubmed_articles.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    logger.info(f"Loaded {len(articles)} articles")
    return articles

def prepare_texts(articles):
    """Prepare text data for embedding"""
    logger.info("Preparing texts for embedding...")
    texts = []
    article_ids = []
    
    for article in articles:
        title = article.get('title', '')
        abstract = article.get('abstract', '')
        text = f"Title: {title}\nAbstract: {abstract}"
        texts.append(text)
        article_ids.append(str(article.get('pmid')))
    
    logger.info(f"Prepared {len(texts)} texts")
    return texts, article_ids

def generate_embeddings(texts, model):
    """Generate embeddings using Sentence Transformer"""
    logger.info("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    logger.info(f"Generated embeddings with shape: {embeddings.shape}")
    return embeddings

def build_faiss_index(embeddings):
    """Build FAISS index"""
    logger.info("Building FAISS index...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings.astype('float32'))
    logger.info(f"FAISS index built with {index.ntotal} vectors")
    return index

def save_index_and_data(index, article_ids, articles):
    """Save index and related data"""
    logger.info("Saving index and data...")
    
    # Save FAISS index
    faiss.write_index(index, 'pubmed_faiss.index')
    logger.info("FAISS index saved")
    
    # Save article IDs
    with open('article_ids.json', 'w', encoding='utf-8') as f:
        json.dump(article_ids, f, ensure_ascii=False, indent=2)
    logger.info("Article IDs saved")

def test_index(index, model, articles, article_ids):
    """Test the generated index"""
    logger.info("Testing index...")
    
    test_query = "health insurance coverage"
    query_embedding = model.encode([test_query])
    
    distances, indices = index.search(query_embedding, 5)
    
    logger.info("Test search results:")
    for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
        if idx < len(articles):
            article = articles[idx]
            logger.info(f"{i+1}. PMID: {article.get('pmid')} (distance: {distance:.3f})")
            logger.info(f"   Title: {article.get('title', '')[:100]}...")

def main():
    """Main function"""
    logger.info("Starting FAISS index regeneration...")
    
    # Remove old files
    remove_old_files()
    
    # Load model
    logger.info("Loading Sentence Transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Load articles
    articles = load_articles()
    
    # Prepare texts
    texts, article_ids = prepare_texts(articles)
    
    # Generate embeddings
    embeddings = generate_embeddings(texts, model)
    
    # Build FAISS index
    index = build_faiss_index(embeddings)
    
    # Save everything
    save_index_and_data(index, article_ids, articles)
    
    # Test the index
    test_index(index, model, articles, article_ids)
    
    logger.info("✅ FAISS index regeneration completed successfully!")

if __name__ == "__main__":
    main() 