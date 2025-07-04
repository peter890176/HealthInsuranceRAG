from utils.s3_helper import S3Helper
import os

def upload_files_to_s3():
    """Upload required files to S3"""
    s3 = S3Helper()
    
    files_to_upload = [
        ("pubmed_faiss.index", "models/pubmed_faiss.index"),
        ("article_ids.json", "data/article_ids.json"),
        ("pubmed_articles.json", "data/pubmed_articles.json")
    ]
    
    for local_path, s3_key in files_to_upload:
        if os.path.exists(local_path):
            print(f"Uploading {local_path} to S3...")
            if s3.upload_file(local_path, s3_key):
                print(f"Successfully uploaded {local_path} to S3")
            else:
                print(f"Failed to upload {local_path}")
        else:
            print(f"File not found: {local_path}")

if __name__ == "__main__":
    upload_files_to_s3() 