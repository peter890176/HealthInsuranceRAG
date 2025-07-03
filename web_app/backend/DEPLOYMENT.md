# Backend Deployment Guide

## Local Development with Docker

### 1. Build and run locally
```bash
# Navigate to backend directory
cd web_app/backend

# Build the Docker image
docker build -t health-insurance-backend .

# Run the container
docker run -p 5000:5000 health-insurance-backend
```

### 2. Using Docker Compose (Recommended for development)
```bash
# Navigate to backend directory
cd web_app/backend

# Build and run with docker-compose
docker-compose up --build

# Run in background
docker-compose up -d --build
```

## Deployment Options

### Option 1: Railway with Docker
1. Connect your GitHub repository to Railway
2. Set Root Directory to `web_app/backend`
3. Railway will automatically detect the Dockerfile and build it

### Option 2: Render with Docker
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set Root Directory to `web_app/backend`
4. Render will use the Dockerfile for deployment

### Option 3: Google Cloud Run
1. Build and push to Google Container Registry
2. Deploy to Cloud Run

### Option 4: AWS ECS/Fargate
1. Build and push to Amazon ECR
2. Deploy to ECS Fargate

## Environment Variables

Set these environment variables in your deployment platform:

```bash
FLASK_ENV=production
FLASK_APP=app.py
```

## Testing the Deployment

After deployment, test your API endpoints:

```bash
# Test search endpoint
curl -X POST https://your-app-url/api/search_with_progress \
  -H "Content-Type: application/json" \
  -d '{"query": "health insurance", "top_k": 5}'

# Test RAG endpoint
curl -X POST https://your-app-url/api/rag_qa_with_progress \
  -H "Content-Type: application/json" \
  -d '{"question": "How does health insurance work?", "top_k": 10}'
```

## Troubleshooting

### Common Issues:

1. **Port binding**: Make sure port 5000 is exposed and accessible
2. **Memory issues**: The FAISS index and models require significant memory
3. **Startup time**: Initial model loading may take several minutes
4. **File permissions**: Ensure data files are readable in the container

### Logs:
```bash
# View container logs
docker logs <container_id>

# View logs with docker-compose
docker-compose logs backend
``` 