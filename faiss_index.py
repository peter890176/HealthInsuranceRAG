#!/usr/bin/env python3
"""
Import embeddings into FAISS and support semantic queries
"""

import numpy as np
import json
import faiss
from sentence_transformers import SentenceTransformer
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

EMBEDDING_FILE = 'output/embeddings/embeddings.npy'
ID_FILE = 'output/embeddings/article_ids.json'
ARTICLES_FILE = 'output/cleaned_data/cleaned_articles.json'
INDEX_FILE = 'output/embeddings/faiss.index'
MODEL_NAME = 'all-MiniLM-L6-v2'


def load_data():
    logger.info('Loading embeddings...')
    embeddings = np.load(EMBEDDING_FILE)
    logger.info(f'Embedding shape: {embeddings.shape}')
    with open(ID_FILE, 'r', encoding='utf-8') as f:
        article_ids = json.load(f)
    with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    return embeddings, article_ids, articles


def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    logger.info(f'Building FAISS index, dimension: {dim}')
    index = faiss.IndexFlatL2(dim)  # L2 distance (can be changed to IndexFlatIP for cosine)
    index.add(embeddings)
    logger.info(f'Index built, vector count: {index.ntotal}')
    return index


def save_faiss_index(index, path):
    faiss.write_index(index, str(path))
    logger.info(f'FAISS index saved: {path}')


def load_faiss_index(path):
    index = faiss.read_index(str(path))
    logger.info(f'FAISS index loaded: {path}')
    return index


def semantic_search(query, index, model, articles, top_k=5):
    # Generate query vector
    query_vec = model.encode([query]).astype('float32')
    # Search
    D, I = index.search(query_vec, top_k)
    results = []
    for rank, idx in enumerate(I[0], 1):
        article = articles[idx]
        results.append({
            'pmid': article.get('pmid'),
            'title': article.get('title', ''),  # Full title
            'abstract': article.get('abstract', ''),  # Full abstract
            'journal': article.get('journal', ''),
            'pub_date': article.get('pub_date', ''),
            'distance': float(D[0][rank-1]),
            'rank': rank
        })
    return results


def main():
    # Load data
    embeddings, article_ids, articles = load_data()
    # Build index
    index = build_faiss_index(embeddings)
    # Save index
    save_faiss_index(index, INDEX_FILE)
    # Load model
    model = SentenceTransformer(MODEL_NAME)
    
    print("🔍 FAISS Semantic Search System")
    print("=" * 50)
    
    while True:
        # Get user input
        query = input("\nEnter search keywords (type 'exit' to quit): ")
        if query.lower() == 'exit':
            break
            
        try:
            top_k = int(input("How many articles to display? (default 10): ") or "10")
        except ValueError:
            top_k = 10
            
        # Execute search
        results = semantic_search(query, index, model, articles, top_k=top_k)
        
        print(f'\n🔍 Query: "{query}"')
        print(f'📊 Found {len(results)} relevant articles')
        print('=' * 80)
        
        for item in results:
            print(f"\n{item['rank']}. PMID: {item['pmid']} (distance: {item['distance']:.3f})")
            print(f"   Journal: {item['journal']}")
            print(f"   Publication Date: {item['pub_date']}")
            print(f"   Title: {item['title']}")
            print(f"   Abstract: {item['abstract'][:300]}..." if len(item['abstract']) > 300 else f"   Abstract: {item['abstract']}")
            print('-' * 80)
        
        print(f"\n✅ Search completed! Displayed {len(results)} articles")
    
    print("\n👋 Thank you for using!")

if __name__ == '__main__':
    main() 