# VeriSource AI

A cybersecurity-focused RAG (Retrieval-Augmented Generation) platform for controlled document verification.

## Architecture

```
FastAPI Backend
├── JWT Authentication + Role-Based Access Control
├── Document Ingestion (PDF parsing, SHA-256 hashing, versioning)
├── ChromaDB Vector Store (per-document isolated collections)
├── fastembed (ONNX Runtime) for embeddings — no PyTorch conflicts
├── Groq LLM (llama-3.1-8b-instant) for controlled generation
└── PostgreSQL (Supabase) for metadata
```

## Phase Status

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Foundation | ✅ |
| 1 | Auth & RBAC | ✅ |
| 2 | Document Ingestion | ✅ |
| 3 | Vector Store | ✅ |
| 4 | Controlled Retrieval | ✅ |
| 5 | Controlled Generation | ✅ |
| 6 | Confidence & Refusal | ⏳ |

## Setup

```bash
cd verisource-ai/backend
pip install -r requirements.txt
cp .env.example .env   # fill in credentials
bash run.sh
```

## Environment Variables

```
DATABASE_URL=postgresql://...
JWT_SECRET=...
JWT_ALGORITHM=HS256
GROQ_API_KEY=gsk_...
```

## Key Design Decisions

- **fastembed** instead of `sentence_transformers` — avoids PyTorch/hnswlib mutex deadlock on Apple Silicon
- **Single-document scoped retrieval** — `get_existing_collection()` never auto-creates collections
- **LLM sees only**: query + evidence text (no scores, metadata, or doc IDs)
- **`INSUFFICIENT_EVIDENCE` sentinel** — model signals lack of evidence, system parses it (model cannot decide refusal)
- **No `--reload`** — single process prevents multiprocess ChromaDB file lock contention

## API Endpoints

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | Public | Register user |
| POST | `/auth/login` | Public | Get JWT token |
| POST | `/ingestion/upload` | Admin | Upload & index PDF |
| POST | `/query/` | Student | Query document |
| GET | `/health` | Public | Health check |
