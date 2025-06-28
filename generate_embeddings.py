#!/usr/bin/env python3
"""
Generate embeddings using Sentence Transformers
Generate semantic vectors for cleaned health insurance literature data
"""

import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from pathlib import Path
import logging
from tqdm import tqdm
import pickle
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Embedding generator"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize generator"""
        self.model_name = model_name
        self.model = None
        self.embeddings = None
        self.article_ids = []
        self.articles = []
        
    def load_model(self):
        """Load Sentence Transformers model"""
        logger.info(f"Loading model: {self.model_name}")
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully, vector dimension: {self.model.get_sentence_embedding_dimension()}")
            return True
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            return False
    
    def load_data(self, input_file):
        """Load cleaned literature data"""
        logger.info(f"Loading data: {input_file}")
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                self.articles = json.load(f)
            logger.info(f"Successfully loaded {len(self.articles):,} articles")
            return True
        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            return False
    
    def prepare_texts(self):
        """Prepare text data"""
        logger.info("Preparing text data...")
        
        texts = []
        for article in self.articles:
            # Combine title and abstract
            title = article.get('title', '')
            abstract = article.get('abstract', '')
            
            # Create text representation
            text = f"Title: {title}\nAbstract: {abstract}"
            texts.append(text)
            
            # Record article ID
            self.article_ids.append(article.get('pmid'))
        
        logger.info(f"Prepared {len(texts)} texts")
        return texts
    
    def generate_embeddings(self, batch_size=32):
        """Generate embeddings"""
        logger.info("Starting embedding generation...")
        
        texts = self.prepare_texts()
        
        # Generate embeddings using Sentence Transformers
        self.embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        logger.info(f"Embedding generation completed, shape: {self.embeddings.shape}")
        return self.embeddings
    
    def save_embeddings(self, output_dir):
        """Save embeddings"""
        logger.info("Saving embeddings...")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Save as numpy format
        np_file = output_dir / "embeddings.npy"
        np.save(np_file, self.embeddings)
        
        # Save article ID mapping
        id_file = output_dir / "article_ids.json"
        with open(id_file, 'w', encoding='utf-8') as f:
            json.dump(self.article_ids, f, ensure_ascii=False, indent=2)
        
        # Save as pickle format (with metadata)
        pickle_data = {
            'embeddings': self.embeddings,
            'article_ids': self.article_ids,
            'model_name': self.model_name,
            'generated_at': datetime.now().isoformat(),
            'embedding_dim': self.embeddings.shape[1],
            'num_articles': len(self.article_ids)
        }
        
        pickle_file = output_dir / "embeddings.pkl"
        with open(pickle_file, 'wb') as f:
            pickle.dump(pickle_data, f)
        
        # Generate report
        report_file = output_dir / "embedding_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("Embedding Generation Report\n")
            f.write("=" * 40 + "\n")
            f.write(f"Generation time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model used: {self.model_name}\n")
            f.write(f"Article count: {len(self.article_ids):,}\n")
            f.write(f"Vector dimension: {self.embeddings.shape[1]}\n")
            f.write(f"Vector shape: {self.embeddings.shape}\n")
            f.write(f"File size: {self.embeddings.nbytes / (1024*1024):.1f} MB\n")
            f.write(f"Average vector norm: {np.mean(np.linalg.norm(self.embeddings, axis=1)):.3f}\n")
        
        logger.info(f"Embeddings saved to: {output_dir}")
        return output_dir
    
    def test_similarity_search(self, test_queries=None):
        """Test similarity search"""
        if test_queries is None:
            test_queries = [
                "health insurance coverage",
                "medical benefits and costs",
                "healthcare policy reform",
                "insurance premium rates",
                "patient access to care"
            ]
        
        logger.info("Testing similarity search...")
        
        # Generate query vectors
        query_embeddings = self.model.encode(test_queries)
        
        # Calculate similarities
        similarities = cosine_similarity(query_embeddings, self.embeddings)
        
        # Find most similar articles
        results = []
        for i, query in enumerate(test_queries):
            # Get top 5 most similar articles
            top_indices = np.argsort(similarities[i])[-5:][::-1]
            
            query_results = []
            for rank, idx in enumerate(top_indices, 1):
                article = self.articles[idx]
                query_results.append({
                    'pmid': article.get('pmid'),
                    'title': article.get('title', '')[:100] + '...',
                    'similarity': float(similarities[i][idx]),
                    'rank': rank
                })
            
            results.append({
                'query': query,
                'top_results': query_results
            })
        
        return results
    
    def save_search_results(self, results, output_dir):
        """Save search test results"""
        output_dir = Path(output_dir)
        
        # Save as JSON
        results_file = output_dir / "similarity_test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Save as CSV
        csv_data = []
        for result in results:
            query = result['query']
            for item in result['top_results']:
                csv_data.append({
                    'query': query,
                    'rank': item['rank'],
                    'pmid': item['pmid'],
                    'title': item['title'],
                    'similarity': item['similarity']
                })
        
        df = pd.DataFrame(csv_data)
        csv_file = output_dir / "similarity_test_results.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')
        
        logger.info(f"Search test results saved: {results_file}, {csv_file}")

def main():
    """Main function"""
    # Set file paths
    input_file = "output/cleaned_data/cleaned_articles.json"
    output_dir = "output/embeddings"
    
    # Load cleaned data
    logger.info(f"Loading data: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    logger.info(f"Loaded {len(articles):,} articles")
    
    # Create embedding generator
    generator = EmbeddingGenerator()
    
    # Load model
    if not generator.load_model():
        return
    
    # Prepare texts
    texts = generator.prepare_texts()
    
    # Generate embeddings
    embeddings = generator.generate_embeddings()
    
    # Save results
    output_path = generator.save_embeddings(output_dir)
    
    # Test similarity search
    test_results = generator.test_similarity_search()
    
    # Save search results
    generator.save_search_results(test_results, output_dir)
    
    # Display result summary
    print(f"\n✅ Embedding generation completed!")
    print(f"📊 Processed articles: {len(articles):,}")
    print(f"🔢 Vector dimension: {embeddings.shape[1]}")
    print(f"📁 Output location: {output_path}")
    print(f"💾 File size: {embeddings.nbytes / (1024*1024):.1f} MB")
    
    print(f"\n🧪 Similarity search test results:")
    for result in test_results:
        print(f"\nQuery: '{result['query']}'")
        for item in result['top_results'][:3]:  # Only show top 3
            print(f"  {item['rank']}. PMID: {item['pmid']} (similarity: {item['similarity']:.3f})")
            print(f"      Title: {item['title']}")

if __name__ == "__main__":
    main() 