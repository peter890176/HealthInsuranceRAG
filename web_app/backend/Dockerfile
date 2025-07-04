# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
# First, install numpy to avoid version conflicts from other packages
RUN pip install --no-cache-dir "numpy<2.0.0,>=1.25.0"
RUN pip install --no-cache-dir -r requirements.txt

# --- Index Generation Step ---
# Copy only the necessary files for building the index
COPY pubmed_articles.json .
COPY build_index.py .

# Run the script to generate the index files
# This ensures the index is built with the exact same library versions
RUN python build_index.py

# --- Application Setup ---
# Copy the rest of the application code
COPY . .

# Expose port for the application
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Start command to run the Flask application
CMD ["python", "app.py"] 