import json
import faiss
import numpy as np
import os
from flask import Flask, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from utils.s3_helper import S3Helper

def ensure_files_exist():
    """Ensure all required files exist, download from S3 if necessary."""
    s3 = S3Helper()
    
    files_to_download = [
        ("pubmed_faiss.index", "models/pubmed_faiss.index"),
        ("article_ids.json", "data/article_ids.json"),
        ("pubmed_articles.json", "data/pubmed_articles.json")
    ]
    
    print("Checking for required files...")
    for local_path, s3_key in files_to_download:
        print(f"Checking {local_path}...")
        if not os.path.exists(local_path):
            print(f"File {local_path} not found, downloading from S3...")
            
            # Ensure target directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            if not s3.download_file(s3_key, local_path):
                raise Exception(f"Failed to download file from S3: {s3_key}")
        else:
            file_size = os.path.getsize(local_path)
            print(f"File {local_path} exists, size: {file_size} bytes")

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Load environment variables
    load_dotenv()

    # --- Load Data and Models into App Context ---
    print("Loading data and models...")
    
    # Ensure all required files exist
    ensure_files_exist()
    
    # 1. Load Sentence Transformer model
    try:
        app.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Sentence Transformer model loaded successfully.")
    except Exception as e:
        print(f"Error loading Sentence Transformer model: {e}")
        raise e

    # 2. Load FAISS index
    try:
        app.index = faiss.read_index('pubmed_faiss.index')
        print("FAISS index loaded successfully.")
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        raise e

    # 3. Load article IDs
    try:
        with open('article_ids.json', 'r') as f:
            app.article_ids = json.load(f)
        print("Article IDs loaded successfully.")
    except Exception as e:
        print(f"Error loading article IDs: {e}")
        raise e

    # 4. Load articles data into a dictionary for O(1) lookups
    try:
        with open('pubmed_articles.json', 'r', encoding='utf-8') as f:
            articles_list = json.load(f)
        
        # Convert list of articles to a dictionary with pmid as key
        app.articles_data_dict = {str(article['pmid']): article for article in articles_list}
        print("Articles data loaded into dictionary successfully.")
    
    except Exception as e:
        print(f"Error loading articles data: {e}")
        raise e

    print("Data loading and model initialization complete.")

    # --- Register Blueprints ---
    from api import api_bp
    app.register_blueprint(api_bp)

    return app

# --- Main Execution ---
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 