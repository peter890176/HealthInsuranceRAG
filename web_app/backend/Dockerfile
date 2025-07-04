# python_version = "3.11"
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git git-lfs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install git-lfs for the repository
RUN git lfs install

# Copy files in an order that optimizes Docker layer caching.
# 1. Copy requirements first.
COPY web_app/backend/requirements.txt .

# 2. Install dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy Git metadata to enable LFS pull.
COPY .git ./.git
COPY .gitattributes .

# 4. Copy the application code.
COPY web_app/backend/ .

# 5. Pull LFS files. This must happen *after* git metadata and app code are copied.
RUN echo "--- Running git lfs pull ---" && \
    git lfs pull && \
    echo "--- git lfs pull completed.---"

# 6. (DEBUG) Verify that the article JSON file was downloaded correctly.
RUN echo "--- Verifying pubmed_articles.json ---" && \
    head -n 5 pubmed_articles.json && \
    echo "--- Verification complete. ---"

# 7. Regenerate the FAISS index inside the container.
RUN echo "--- Regenerating FAISS index ---" && \
    python regenerate_index.py && \
    echo "--- FAISS index regeneration complete. ---"

# 8. (DEBUG) Verify that the index file was created.
RUN echo "--- Verifying created files ---" && \
    ls -lha . && \
    echo "--- Verification complete. ---"

# Set the command to run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"] 