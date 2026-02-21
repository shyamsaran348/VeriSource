# VeriSource AI

<div align="center">

**A governance-first, evidence-only document verification platform powered by RAG + Controlled LLM Generation.**

*Built to prove that AI can answer questions from documents — without hallucinating, without guessing, without mixing sources.*

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![ChromaDB](https://img.shields.io/badge/ChromaDB-1.5.1-orange)
![Groq](https://img.shields.io/badge/LLM-Groq%20llama--3.1--8b-purple)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

</div>

---

## What Is VeriSource?

VeriSource is a **Retrieval-Augmented Generation (RAG) backend** designed for high-stakes document verification — policy compliance, academic regulation lookup, and research synthesis.

Unlike general-purpose chatbots, VeriSource enforces strict architectural constraints:

- ✅ **Evidence-only answers** — LLM sees *only* extracted document chunks + the query
- ✅ **Single-document scope** — queries are strictly isolated to one document's vector collection
- ✅ **No hallucination path** — model cannot generate answers without retrieved evidence
- ✅ **Governance-first** — mode mismatch, inactive versions, and missing collections are blocked *before* retrieval
- ✅ **Role-enforced** — students query, admins ingest. No overlap.
- ✅ **`INSUFFICIENT_EVIDENCE` sentinel** — model signals when evidence doesn't support the query; *refusal is enforced by the system, not the model*

---

## Phase Progress

| Phase | Description | Status |
|:---:|---|:---:|
| 0 | Foundation — FastAPI, PostgreSQL, project structure | ✅ Complete |
| 1 | Auth & RBAC — JWT, admin/student roles | ✅ Complete |
| 2 | Document Ingestion — PDF parsing, SHA-256, versioning | ✅ Complete |
| 3 | Vector Store — ChromaDB per-document collections, fastembed | ✅ Complete |
| 4 | Controlled Retrieval — governance enforcement, evidence extraction | ✅ Complete |
| 5 | Controlled Generation — Groq LLM, evidence-only prompts | ✅ Complete |
| 6 | Confidence & Refusal Engine | ⏳ Planned |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT                                   │
│              (Swagger UI / Frontend / API Consumer)             │
└─────────────────────┬───────────────────────────────────────────┘
                      │  HTTP
┌─────────────────────▼───────────────────────────────────────────┐
│                   FastAPI Backend                               │
│                                                                 │
│  ┌──────────────┐  ┌────────────────────────────────────────┐  │
│  │  Auth Layer  │  │           Query Pipeline               │  │
│  │              │  │                                        │  │
│  │  JWT Tokens  │  │  1. JWT Verify                         │  │
│  │  bcrypt hash │  │  2. Role check (student only)          │  │
│  │  Admin RBAC  │  │  3. Document exists? (PostgreSQL)       │  │
│  └──────────────┘  │  4. Mode match? Active version?        │  │
│                    │  5. Vector collection exists?           │  │
│  ┌──────────────┐  │  6. Embed query → retrieve top-K       │  │
│  │  Ingestion   │  │  7. Extract evidence (chunk_id check)  │  │
│  │  Pipeline    │  │  8. Conflict detection (variance)      │  │
│  │              │  │  9. Groq LLM (evidence text only)      │  │
│  │  PDF → Text  │  │  10. Parse INSUFFICIENT_EVIDENCE       │  │
│  │  Chunk       │  │  11. Return structured response        │  │
│  │  Embed       │  └────────────────────────────────────────┘  │
│  │  ChromaDB    │                                               │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
         │                           │
┌────────▼──────────┐    ┌───────────▼──────────────┐
│   PostgreSQL      │    │      ChromaDB             │
│   (Supabase)      │    │   (Persistent Vector DB)  │
│                   │    │                           │
│  - users          │    │  Collections:             │
│  - documents      │    │  doc_{uuid_a}/            │
│    (name, mode,   │    │  doc_{uuid_b}/            │
│     version,      │    │  doc_{uuid_c}/            │
│     is_active,    │    │   ← One per document      │
│     hash)         │    │   ← Never shared          │
└───────────────────┘    └───────────────────────────┘
```

---

## Query Flow (Detailed)

```
POST /query/
  │
  ├─ 1. JWT decode → get username
  ├─ 2. Role check: student? → OK | admin? → 403
  ├─ 3. DB lookup: document_id exists? → 404 if not
  ├─ 4. Governance:
  │     ├─ document.mode == request.mode? → 400 if not
  │     └─ mode=="policy" and not is_active? → 400
  ├─ 5. Vector isolation:
  │     └─ get_existing_collection() → 404 if missing (NEVER auto-creates)
  ├─ 6. fastembed: embed query → 384-dim vector
  ├─ 7. ChromaDB: query(top-5 chunks, include distances + metadata)
  ├─ 8. Evidence extraction:
  │     └─ chunk_id missing from metadata? → 500 (integrity failure)
  ├─ 9. Conflict detection: max_score - min_score > threshold?
  │     ├─ policy threshold: 0.35 (strict)
  │     └─ research threshold: 0.60 (tolerant)
  ├─ 10. Groq LLM call:
  │      ├─ system: mode-specific governance prompt
  │      ├─ user: query + evidence TEXT only
  │      └─ LLM never sees: scores, chunk_ids, doc_id, conflict flag
  ├─ 11. Response parser:
  │      └─ "INSUFFICIENT_EVIDENCE" in output? → answer=null, flag=true
  └─ 12. Return QueryResponse
```

---

## Technology Stack

| Layer | Technology | Why |
|---|---|---|
| **API Framework** | FastAPI | Async, auto-docs, dependency injection |
| **Metadata DB** | PostgreSQL (Supabase) | Document records, user accounts, versioning |
| **Vector DB** | ChromaDB 1.5.1 | Per-document collection isolation, persistent |
| **Embeddings** | **fastembed** (ONNX Runtime) | *Replaces PyTorch* — eliminates Apple Silicon mutex deadlock with hnswlib |
| **LLM** | Groq `llama-3.1-8b-instant` | Fast inference, deterministic (temp=0), evidence-bounded |
| **Auth** | JWT (python-jose) + bcrypt | Token-based, role-enforced |
| **PDF Parsing** | pypdf | Text extraction from uploaded PDFs |

> **Why fastembed instead of sentence-transformers?**
> `sentence_transformers` depends on PyTorch, which uses an OpenMP thread pool. On Apple Silicon (ARM64), this clashes with ChromaDB's hnswlib C++ vector index — both use abseil-cpp mutexes, causing a native deadlock (`mutex.cc Lock blocking`). `fastembed` uses ONNX Runtime which has an independent thread pool — zero conflict.

---

## Project Structure

```
VeriSource/
├── README.md
├── .gitignore
└── verisource-ai/
    └── backend/
        ├── run.sh                    # Launch server (sets thread env vars correctly)
        ├── requirements.txt
        └── app/
            ├── main.py               # FastAPI app, ML_EXECUTOR, startup warmup
            ├── core/
            │   ├── config.py         # Settings (env vars)
            │   ├── dependencies.py   # require_admin, require_student
            │   ├── security.py       # JWT creation/validation
            │   └── logging.py
            ├── auth/
            │   ├── router.py         # POST /auth/register, /auth/login
            │   ├── service.py        # create_user, authenticate_user
            │   └── schemas.py
            ├── ingestion/
            │   ├── router.py         # POST /ingestion/upload (admin only)
            │   ├── parser.py         # PDF text extraction
            │   └── hasher.py         # SHA-256 file hashing
            ├── documents/
            │   ├── models.py         # Document SQLAlchemy model
            │   └── service.py        # get_document_by_id, validate_document_access
            ├── users/
            │   └── models.py         # User SQLAlchemy model
            ├── rag/
            │   ├── embeddings.py     # fastembed TextEmbedding (ONNX)
            │   ├── vector_store.py   # ChromaDB client, get_existing_collection
            │   ├── chunker.py        # Sliding window text chunking
            │   ├── retriever.py      # Single-document vector search
            │   ├── evidence.py       # Evidence extraction + chunk_id validation
            │   └── conflict.py       # Variance-based conflict detection
            ├── llm/
            │   ├── provider.py       # Groq API call (evidence-only prompt)
            │   └── response_parser.py # INSUFFICIENT_EVIDENCE detection
            ├── query/
            │   ├── router.py         # POST /query/ (student only)
            │   └── schemas.py        # QueryRequest, QueryResponse, EvidenceBlock
            └── db/
                ├── base.py
                └── session.py
```

---

## API Reference

### Authentication

#### `POST /auth/register`
Register a new user.

```json
// Request body
{
  "username": "john_doe",
  "password": "secure_password",
  "role": "student"   // or "admin"
}

// Response 200
{
  "message": "User registered successfully",
  "username": "john_doe",
  "role": "student"
}
```

#### `POST /auth/login`
Login with form data, receive JWT.

```
Content-Type: application/x-www-form-urlencoded
username=john_doe&password=secure_password

// Response 200
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

---

### Document Ingestion

#### `POST /ingestion/upload`
Upload and index a PDF document. **Admin only.**

```
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

Fields:
  name       (str)  — document name, e.g. "UG_Regulations"
  mode       (str)  — "policy" or "research"
  version    (str)  — e.g. "v1", "2024"
  authority  (str)  — issuing authority
  file       (pdf)  — the PDF file

// Response 200
{
  "document_id": "f850a155-dc4b-4c07-ba95-bd72a2abf1fb",
  "message": "Document uploaded and indexed successfully",
  "chunks_created": 182
}
```

> **Versioning rule:** When a new version of a policy document is uploaded (same `name` + `mode="policy"`), all previous versions are automatically set to `is_active=False`. Only the latest version can be queried.

---

### Query

#### `POST /query/`
Query a document. **Student only.**

```json
// Request
Authorization: Bearer <student_token>

{
  "mode": "policy",
  "document_id": "f850a155-dc4b-4c07-ba95-bd72a2abf1fb",
  "query": "What is the attendance requirement for students?"
}

// Response 200
{
  "document_id": "f850a155-dc4b-4c07-ba95-bd72a2abf1fb",
  "mode": "policy",
  "evidence": [
    {
      "chunk_id": "f850a155-dc4b-4c07-ba95-bd72a2abf1fb_12",
      "text": "Every student is expected to attend a minimum of 75% of classes...",
      "score": 0.8732
    }
  ],
  "conflict_detected": false,
  "answer": "Students are required to maintain a minimum attendance of 75% in all subjects.",
  "model_flag_insufficient": false
}
```

**Error responses:**

| Status | Condition |
|---|---|
| 400 | Mode mismatch (policy doc queried as research) |
| 400 | Inactive policy version |
| 400 | Empty query string |
| 401 | No or invalid JWT token |
| 403 | Admin trying to query (student role required) |
| 404 | Document not found |
| 404 | Vector collection not found (document ingested but collection deleted) |
| 500 | Chunk metadata integrity failure (chunk_id missing) |

---

### Health

#### `GET /health`
```json
{
  "status": "healthy",
  "app": "VeriSource AI",
  "version": "0.1.0"
}
```

---

## Setup & Running

### Prerequisites

- Python 3.12+
- PostgreSQL (or Supabase free tier)
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

```bash
git clone https://github.com/shyamsaran348/VeriSource.git
cd VeriSource/verisource-ai/backend

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in `verisource-ai/backend/`:

```env
APP_NAME=VeriSource AI
DEBUG=True
VERSION=0.1.0

DATABASE_URL=postgresql://user:password@host:5432/dbname
JWT_SECRET=your-very-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

GROQ_API_KEY=gsk_...
```

### Running the Server

```bash
# Always use run.sh — NOT uvicorn directly
bash run.sh
```

> **Why `run.sh`?** Thread env vars (`OMP_NUM_THREADS=1`, etc.) must be exported at OS level **before** Python starts. Setting them inside `main.py` is too late — native C++ libraries (hnswlib, OpenMP) initialize their thread pools on first import. `run.sh` also disables `--reload` to prevent multiprocess ChromaDB file lock contention.

Server starts at `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`

---

## Governance Rules (Enforced in Code)

| Rule | Enforcement Point | Effect on Violation |
|---|---|---|
| Student-only query | `require_student` dependency | `403 Forbidden` |
| Document must exist | `get_document_by_id()` | `404 Not Found` |
| Mode must match document | `validate_document_access()` | `400 Bad Request` |
| Policy must be active version | `validate_document_access()` | `400 Bad Request` |
| Vector collection must exist | `get_existing_collection()` | `404 Not Found` |
| Collection never auto-created during retrieval | `get_existing_collection()` | (enforced by design) |
| chunk_id must be in metadata | `extract_evidence()` | `500 Internal Error` |
| LLM receives only query + text | `generate_answer()` | (enforced by design) |
| Empty query blocked | Pydantic `field_validator` | `422 Unprocessable` |

---

## Known Design Decisions

### Apple Silicon Mutex Fix
On macOS ARM64, `sentence_transformers` (PyTorch) and ChromaDB (hnswlib) share abseil-cpp mutex infrastructure, causing a native deadlock. Solution: replaced PyTorch with **fastembed** (ONNX Runtime), which has an independent thread pool.

### Single-Thread ML Executor
A `ThreadPoolExecutor(max_workers=1)` named `ML_EXECUTOR` is created at startup and shared across the startup warmup and all ingestion requests. This serializes all native C++ library operations onto one thread, preventing inter-library mutex races.

### Per-Document Vector Collections
Each document gets its own ChromaDB collection named `doc_{document_id}`. Retreival queries only that one collection — there is no cross-document search path in the codebase.

### LLM Prompt Architecture
The LLM system prompt varies by mode:
- **Policy mode** — deterministic language required: *"must", "shall", "is required"*
- **Research mode** — probabilistic language required: *"suggests", "indicates", "may imply"*

Both prompts instruct the model to output exactly `INSUFFICIENT_EVIDENCE` (not any paraphrase) when evidence doesn't support the query.

---

## Test Results

All governance tests run automatically. Phase 4 and 5 both achieved **31/31 tests passed**.

```
Phase 4 — Controlled Retrieval: 31/31 ✅
Phase 5 — Controlled Generation: 31/31 ✅
```

Test categories covered:
- Access control (student/admin/unauthenticated)
- Document governance (mode mismatch, inactive version, nonexistent doc)
- Vector isolation (no auto-create, cross-document contamination check)
- Evidence structure (chunk_id, score type, no extra fields)
- Conflict detection (variance-based, mode-aware thresholds)
- LLM security (scores/metadata/doc_id never exposed to model)
- Failure safety (restart stability, corrupt metadata handling)

---

## License

MIT — see [LICENSE](LICENSE)
