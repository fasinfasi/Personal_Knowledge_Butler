# Personal Knowledge Butler

Personal Knowledge Butler is a self-hosted Document Q&A assistant that helps you search and query your personal documents (PDFs, Word files, spreadsheets, text, notes, emails, etc.). It extracts text from uploaded files, creates embeddings, persists a vector index (Chroma), and returns natural-language answers by retrieving relevant chunks and synthesizing responses.

This repository provides a developer-focused local stack with a FastAPI backend and a Streamlit UI for experimentation and small-scale use.

**Status:** Working prototype (retrieval + heuristic synthesis). The codebase also contains experimental RAG helpers and example vector DB artifacts for testing.

---

**Repository layout**

- `backend/` — FastAPI application, API routes, ingestion, document loaders, vector store logic, and QA modules.
- `frontend/` — Streamlit UI for uploading documents and asking questions.
- `data_pipeline/`, `chroma_db/` — sample uploads and persisted Chroma vector DB artifacts (included for convenience and testing).

---

**Main capabilities**

- Upload and index documents: support for PDF, DOCX, XLSX, TXT, MD (extract + chunk).
- Build and persist a vector index (Chroma) using Hugging Face sentence-transformer embeddings.
- Retrieve relevant chunks and rerank using TF–IDF and heuristics to produce concise answers.
- Simple Streamlit UI and FastAPI endpoints for integration and automation.

---

**Architecture overview**

- Frontend: `frontend/app.py` — Streamlit UI that uploads files to the backend and queries the index.
- Backend: `backend/main.py` — FastAPI app; `backend/api/routes.py` exposes upload and query endpoints.
- Document loaders: `backend/core/document_loader.py` (simple) and `backend/rag_pipeline/document_loader.py` (advanced PDF extraction and chunking strategies).
- Vector store: `backend/core/vector_store.py` and `backend/rag_pipeline/vectorstore.py` — build and load a Chroma index (persisted under `chroma_db/`).
- QA & response generation: `backend/core/qa_engine.py` (retrieval + TF–IDF rerank) and `backend/rag_pipeline/llm_response.py` (advanced heuristics). Note: the active API path currently uses heuristic synthesis rather than calling a generative LLM.

---

**Quickstart (development)**

Prerequisites

- Python 3.10+ (confirm exact compatibility with pinned dependencies)
- Git

Install dependencies (run from the `backend` directory):

```powershell
cd c:\Users\HP\Repositories\Projects\Personal_Knowledge_Butler\backend
python -m pip install -r requirements.txt
```

Start the backend (development):

```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Start the Streamlit UI (separate shell):

```powershell
cd c:\Users\HP\Repositories\Projects\Personal_Knowledge_Butler\frontend
streamlit run app.py
```

Open the UI at `http://localhost:8501` and the FastAPI interactive docs at `http://localhost:8000/docs`.

---

**API endpoints (brief)**

- `GET /` — service root message
- `GET /health` — simple health check
- `POST /upload` — upload a file (multipart `file`), saved to `uploads/` and then indexed
- `GET /query?query=...` — query the index and return a synthesized answer

Refer to `backend/api/routes.py` for the exact implementation.

---

**Configuration**

- The backend reads environment variables from `backend/config/.env` by default. Key variables:
  - `HUGGINGFACEHUB_API_TOKEN` — API token for Hugging Face (if required for private models or remote calls)
  - `MODEL_NAME`, `TEMPERATURE`, `MAX_TOKENS` — placeholders for LLM integration (not used in the default query path)

Security note: Do not commit secrets. The token present in `backend/config/.env` should be removed from the repository and rotated.

Recommended steps before publishing this repo publicly:
1. Remove secrets from the repo and rotate keys.
2. Add `backend/config/.env` to `.gitignore` and include a `backend/config/.env.example` instead.

---

**Operational notes & known limitations**

- The current ingestion flow recreates the entire `VECTOR_DB_DIR` on each upload (the implementation deletes the index directory before creating a new index). This is destructive — adapt the ingestion code for incremental indexing if you want to preserve previously indexed documents.
- Query answers are produced by retrieval and heuristic synthesis (TF–IDF and rule-based extractors). If you want generative answers (LLM-based), integrate an LLM call in the response path (code scaffolding exists in `rag_pipeline`).
- CORS is configured permissively for development. Restrict origins and add authentication for production.
- The repository currently contains persisted Chroma DB artifacts and uploaded documents. Remove private data and large binary artifacts from version control to protect privacy and reduce repository size.

---

**Security & privacy**

- Immediately remove any committed API tokens and rotate them.
- Remove uploaded documents and vector DB artifacts that contain private information from version control and add them to `.gitignore`.
- Add authentication and authorization to API endpoints before making the service publicly accessible.

---

**Next steps / suggested improvements**

- Create `.env.example` with configuration keys and add `.env` to `.gitignore`.
- Replace the destructive index creation with incremental ingestion or per-document/per-user index directories.
- Consolidate duplicate modules (`core` vs `rag_pipeline`) to reduce maintenance overhead; make the API use the robust loader if desired.
- Add optional LLM-based answer generation with configurable model backends and cost controls.
- Add Dockerfile and deployment manifests for reproducible deployments.

---

**Contributing**

Contributions are welcome. Suggested workflow:

1. Open an issue describing the feature or bug.
2. Create a branch for your change and include tests where possible.
3. Submit a pull request and describe the change in detail.

---
Follow Me🚶🏻‍➡️
