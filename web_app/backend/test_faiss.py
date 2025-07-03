import faiss
import os

print(f"FAISS version: {faiss.__version__}")
print(f"FAISS build info: {faiss.get_compile_options()}")

# Check if index file exists
index_file = 'pubmed_faiss.index'
if os.path.exists(index_file):
    print(f"Index file exists: {index_file}")
    print(f"Index file size: {os.path.getsize(index_file) / (1024*1024):.2f} MB")
    
    try:
        # Try to read the index
        index = faiss.read_index(index_file)
        print(f"Successfully loaded index with {index.ntotal} vectors")
    except Exception as e:
        print(f"Error loading index: {e}")
else:
    print(f"Index file not found: {index_file}") 