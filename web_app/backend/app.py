import json
import faiss
import numpy as np
import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

def download_file_from_github(file_path, local_path):
    """Download a file from GitHub repository."""
    # GitHub raw content URL (replace with your actual repository)
    github_url = f"https://raw.githubusercontent.com/peter890176/HealthInsuranceRAG/main/{file_path}"
    
    print(f"Downloading {file_path} from GitHub...")
    print(f"URL: {github_url}")
    
    try:
        response = requests.get(github_url, stream=True, timeout=300)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        print(f"File size: {total_size} bytes")
        
        with open(local_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"Download progress: {progress:.1f}%")
        
        print(f"Downloaded {file_path} successfully.")
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {file_path}: {e}")
        raise e

def ensure_files_exist():
    """Ensure all required files exist, download if necessary."""
    files_to_download = [
        ("web_app/backend/pubmed_faiss.index", "pubmed_faiss.index"),
        ("web_app/backend/article_ids.json", "article_ids.json"),
        ("web_app/backend/pubmed_articles.json", "pubmed_articles.json")
    ]
    
    print("Checking for required files...")
    for github_path, local_path in files_to_download:
        print(f"Checking {local_path}...")
        if not os.path.exists(local_path):
            print(f"File {local_path} not found, downloading...")
            download_file_from_github(github_path, local_path)
        else:
            file_size = os.path.getsize(local_path)
            print(f"File {local_path} exists, size: {file_size} bytes")

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Load environment variables from .env file
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
    # Import and register blueprints after data is loaded
    from api import api_bp
    app.register_blueprint(api_bp)

    return app

# --- Main Execution ---
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 