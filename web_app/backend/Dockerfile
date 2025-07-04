# python_version = "3.11"
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy specific files explicitly to ensure they are included
COPY app.py .
COPY api/ ./api/
COPY utils/ ./utils/
COPY pubmed_faiss.index .
COPY article_ids.json .
COPY pubmed_articles.json .

# Set the command to run the application using Gunicorn for production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:create_app()"] 