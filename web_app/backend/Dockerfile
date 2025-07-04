# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# --- Git LFS Installation ---
# Install Git and Git LFS to fetch large files
RUN apt-get update && \
    apt-get install -y git git-lfs && \
    rm -rf /var/lib/apt/lists/*
RUN git lfs install

# --- Application Setup ---
# Copy the entire repository content first
COPY . .

# Fetch LFS files
# This command pulls down the actual content of files tracked by Git LFS
RUN git lfs fetch --all && git lfs pull

# Install Python dependencies
# Now that all files are present, install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir "numpy<2.0.0,>=1.25.0" && \
    pip install --no-cache-dir -r requirements.txt

# --- Index Generation ---
# Run the script to generate the index files using the full data
RUN python build_index.py

# Expose port for the application
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Start command to run the Flask application
CMD ["python", "app.py"] 