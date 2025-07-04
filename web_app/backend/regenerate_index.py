#!/usr/bin/env python3
"""
Non-interactive script to regenerate FAISS index for deployment builds.
Includes a salt to ensure the generated index content changes.
"""
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import logging
import os
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
ARTICLES_INPUT_FILE = 'pubmed_articles.json'
FAISS_OUTPUT_FILE = 'pubmed_faiss.index'
IDS_OUTPUT_FILE = 'article_ids.json'
MODEL_NAME = 'all-MiniLM-L6-v2'

def load_articles():
    """Loads articles from the source JSON file."""
    logger.info(f"Loading articles from {ARTICLES_INPUT_FILE}...")
    if not os.path.exists(ARTICLES_INPUT_FILE):
        logger.error(f"Source articles file not found: {ARTICLES_INPUT_FILE}")
        raise FileNotFoundError(f"Required data file not found: {ARTICLES_INPUT_FILE}")
    with open(ARTICLES_INPUT_FILE, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    logger.info(f"Successfully loaded {len(articles)} articles.")
    return articles

def prepare_texts(articles):
    """Prepares texts and extracts PMIDs for embedding."""
    logger.info("Preparing texts for embedding...")
    texts = []
    article_ids = []
    
    # Add a "salt" to the first article to force a content change
    # This ensures the embedding and index will be different each time
    salt = f" [build_salt: {time.time()}]"
    
    for i, article in enumerate(articles):
        title = article.get('title', '')
        abstract = article.get('abstract', '')
        text = f"Title: {title}\nAbstract: {abstract}"
        if i == 0:
            text += salt
            logger.info(f"Added salt to first article to ensure unique index.")
            
        texts.append(text)
        article_ids.append(str(article.get('pmid')))
        
    logger.info(f"Prepared {len(texts)} texts for embedding.")
    return texts, article_ids

def generate_embeddings(texts, model):
    """Generates embeddings for the given texts."""
    logger.info("Generating embeddings... This may take a while.")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    logger.info(f"Embedding generation complete. Shape: {embeddings.shape}")
    return embeddings

def build_and_save_index(embeddings, article_ids):
    """Builds and saves the FAISS index and article IDs."""
    logger.info("Building and saving FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    
    # Save FAISS index
    faiss.write_index(index, FAISS_OUTPUT_FILE)
    logger.info(f"FAISS index with {index.ntotal} vectors saved to {FAISS_OUTPUT_FILE}")
    
    # Save corresponding article IDs
    with open(IDS_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(article_ids, f, ensure_ascii=False, indent=2)
    logger.info(f"Article IDs saved to {IDS_OUTPUT_FILE}")

def main():
    """Main execution function."""
    logger.info("--- Starting FAISS Index Regeneration for Deployment ---")
    
    # 1. Load the Sentence Transformer model
    logger.info(f"Loading Sentence Transformer model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    # 2. Load the source articles
    articles = load_articles()
    
    # 3. Prepare texts with a salt to ensure uniqueness
    texts, article_ids = prepare_texts(articles)
    
    # 4. Generate embeddings
    embeddings = generate_embeddings(texts, model)
    
    # 5. Build and save the index and IDs
    build_and_save_index(embeddings, article_ids)
    
    logger.info("--- ✅ FAISS Index Regeneration Completed Successfully ---")

if __name__ == "__main__":
    main() 