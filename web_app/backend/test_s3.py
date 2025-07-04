from utils.s3_helper import S3Helper
import os

def test_s3():
    print("Testing S3 connection...")
    s3 = S3Helper()
    
    print(f"Bucket: {s3.bucket_name}")
    print(f"Region: {s3.region}")
    
    # Test downloading a file
    print("\nTesting file download...")
    if s3.download_file("models/pubmed_faiss.index", "test_pubmed_faiss.index"):
        print("Successfully downloaded pubmed_faiss.index")
        # Clean up
        os.remove("test_pubmed_faiss.index")
    else:
        print("Failed to download pubmed_faiss.index")

if __name__ == "__main__":
    test_s3() 