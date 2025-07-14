# PubMed Health Insurance Semantic Search & RAG QA Platform

> Developed with Gemini 2.5 Pro assistance and verified by the author.

A full-stack AI-powered platform for semantic search and retrieval-augmented generation (RAG) Q&A on PubMed health insurance literature.

---

## Live Demo

[https://hirag.netlify.app/rag](https://hirag.netlify.app/rag)

---

## Features

- **Semantic Search**: Fast, vector-based search over PubMed articles using FAISS and Sentence Transformers.
- **RAG Q&A**: Ask natural language questions and get AI-generated answers with supporting articles.
- **Multilingual Support**: Automatic translation for non-English queries (e.g., Chinese).
- **Streaming Progress**: Real-time progress updates for long-running queries.
- **Responsive UI**: Mobile-friendly, modern Material-UI design.
- **Cloud Storage**: Large data files (FAISS index, articles) are loaded from AWS S3.
- **Easy Deployment**: Dockerized backend, Netlify frontend, and deployment guides for Railway/Render.

---

## Project Structure

```
root/
├── mesh_health_insurance_crawler.py   # PubMed crawler (data preparation)
├── web_app/
│   ├── backend/                      # Flask API, FAISS, S3, Docker
│   └── frontend/                     # React, Material-UI, Netlify
├── output/                           # Data output (gitignored)
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
```

---

## Backend

- **API**: Flask REST API for search, RAG Q&A, translation, and health check.
- **Vector Search**: FAISS index for fast semantic search.
- **RAG Pipeline**: Sentence Transformers + OpenAI/HuggingFace for answer generation.
- **S3 Integration**: Large files are loaded from AWS S3 at startup.
- **Dockerized**: Ready for Railway, Render, or any Docker-compatible cloud.

### Run Locally

```bash
cd web_app/backend
docker-compose up --build
# or
docker build -t health-insurance-backend .
docker run -p 5000:5000 health-insurance-backend
```

### API Endpoints

- `POST /api/search_with_progress`
- `POST /api/rag_qa_with_progress`
- `POST /api/translate`
- `GET  /api/health`

See `web_app/backend/api/routes.py` for details.

---

## Frontend

- **Framework**: React + Material-UI
- **Pages**: Semantic Search, RAG Q&A
- **Features**: Streaming progress, responsive design, PubMed article cards, markdown rendering
- **Deployment**: Netlify-ready

### Run Locally

```bash
cd web_app/frontend
npm install
npm start
```

### Build for Production

```bash
npm run build
```

---

## Data Preparation

- Use `mesh_health_insurance_crawler.py` to crawl PubMed and generate data files.
- Use `generate_embeddings.py` and `faiss_index.py` to create embeddings and FAISS index.
- Upload large files to S3 using `upload_to_s3.py`.

---

## Deployment

- **Backend**: Deploy with Docker (Railway, Render, etc.)
- **Frontend**: Deploy with Netlify (see `netlify.toml`)
- **Environment Variables**: Set S3, OpenAI, and other keys as needed.

See `web_app/backend/DEPLOYMENT.md` for detailed instructions.

---

## License

MIT License

---

## Acknowledgements

Developed with Gemini 2.5 Pro assistance and verified by the author.

---

## Contact

For questions or issues, please open an issue in the repository. 