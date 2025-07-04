# python_version = "3.11"
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code, including the pre-built index
COPY . .

# Set the command to run the application using Gunicorn for production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:create_app()"] 