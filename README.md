# VeriSource AI

<div align="center">

**A governance-first, evidence-only document verification platform powered by RAG + Controlled LLM Generation.**

*Built to prove that AI can answer questions from documents — without hallucinating, without guessing, without mixing sources.*

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18.3.1-61dafb?logo=react)
![ChromaDB](https://img.shields.io/badge/ChromaDB-1.5.1-orange)
![Groq](https://img.shields.io/badge/LLM-Groq%20llama--3.1--8b-purple)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

</div>

---

## What Is VeriSource?

VeriSource is a **full-stack Retrieval-Augmented Generation (RAG) platform** designed for high-stakes document verification — policy compliance, academic regulation lookup, and research synthesis.

Unlike general-purpose chatbots, VeriSource enforces strict architectural constraints:

- ✅ **Evidence-only answers** — LLM sees *only* extracted document chunks + the query
- ✅ **Mathematical Confidence Engine** — Strict vector distance cutoffs enforce "Hard Blocks" before the LLM can hallucinate
- ✅ **Single-document scope** — queries are strictly isolated to one document's vector collection
- ✅ **Governance-first** — mode mismatch, inactive versions, and missing collections are blocked *before* retrieval
- ✅ **Audit Trail** — Non-repudiable cryptographic logging of every query, chunk retrieved, and LLM decision
- ✅ **Role-enforced** — students query, admins ingest. No overlap.

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
| 6 | Confidence & Refusal Engine — Mathematical similarity threshold enforcement | ✅ Complete |
| 7 | Audit & Compliance — Transaction hashing, DB logging for every decision | ✅ Complete |
| 8 | Frontend Console — React SPA, Verification UI, Admin dashboards | ✅ Complete |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        REACT FRONTEND                           │
│     (Student Verification Console / Admin Ingestion Portal)     │
└─────────────────────┬───────────────────────────────────────────┘
                      │  HTTP (JWT Auth)
┌─────────────────────▼───────────────────────────────────────────┐
│                   FastAPI Backend                               │
│                                                                 │
│  ┌──────────────┐  ┌────────────────────────────────────────┐  │
│  │  Auth Layer  │  │           Query Pipeline               │  │
│  │              │  │                                        │  │
│  │  JWT Tokens  │  │  1. Role & Access Checks               │  │
│  │  bcrypt hash │  │  2. Strict Vector Isolation            │  │
│  │  Admin RBAC  │  │  3. ChromaDB Retrieval (Top-K)         │  │
│  └──────────────┘  │  4. FastEmbed Distance Calculation     │  │
│                    │  5. Variance Conflict Detection        │  │
│  ┌──────────────┐  │  6. Governance Engine Decision Loop    │  │
│  │  Ingestion   │  │  7. Controlled Groq LLM Synthesis      │  │
│  │  Pipeline    │  │  8. Audit DB Logging (Tx Hash)         │  │
│  │              │  │  9. JSON UI Payload Generation         │  │
│  │  PDF → Text  │  └────────────────────────────────────────┘  │
│  │  Chunk/Embed │                                               │
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
│  - audit_logs     │    │  doc_{uuid_b}/            │
└───────────────────┘    └───────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Why |
|---|---|---|
| **Frontend UI** | React 18, Vite, Tailwind CSS | Fast SPA, modern styling, dynamic components |
| **Animation SDK** | Framer Motion | Fluid micro-animations for premium UX |
| **API Framework** | FastAPI | Async, auto-docs, dependency injection |
| **Metadata DB** | PostgreSQL (Supabase) | Document records, user accounts, audit trails |
| **Vector DB** | ChromaDB 1.5.1 | Per-document collection isolation, persistent |
| **Embeddings** | **fastembed** (ONNX Runtime) | Strict vector score spread, avoids PyTorch mutex deadlock |
| **LLM** | Groq `llama-3.1-8b-instant` | Fast inference, deterministic (temp=0), zero-escape prompts |
| **Auth** | JWT (python-jose) + bcrypt | Token-based, role-enforced backend auth |

---

## Project Structure

```
VeriSource/
├── frontend/                 # React UI Workspace
│   ├── src/
│   │   ├── auth/             # ProtectedRoutes, AuthContext
│   │   ├── components/       # DecisionCards, EvidencePanels
│   │   ├── layouts/          # Admin/Student specific Navbars
│   │   ├── pages/            # Verification Console, Dashboards
│   │   └── services/         # Axios API Wrappers
│   └── package.json
└── verisource-ai/
    └── backend/
        ├── run.sh            # Launch server (OS thread configs)
        ├── requirements.txt
        └── app/
            ├── main.py       # FastAPI application and ML warmup
            ├── auth/         # JWT Token Auth
            ├── ingestion/    # Admin PDF Uploads
            ├── decision/     # Phase 6 Governance Engine (Refusals)
            ├── audit/        # Phase 7 DB Logging
            ├── documents/    # State & Versioning
            ├── rag/          # Vector Store, Embeddings, Conflicts
            └── llm/          # Groq API System Prompts
```

---

## Setup & Running

### Prerequisites

- Node.js v18+ (for Frontend)
- Python 3.12+ (for Backend)
- PostgreSQL Database
- Groq API Key

### Backend Setup

```bash
cd verisource-ai/backend
pip install -r requirements.txt

# Create .env file with DATABASE_URL, JWT_SECRET, GROQ_API_KEY
# MUST launch using run.sh to prevent SQLite/C++ deadlock
./run.sh
```

### Frontend Setup

```bash
cd frontend
npm install

# Start Vite dev server
npm run dev
```

---

## Governance Rules (Enforced in Code)

| Rule | Enforcement Point | Effect on Violation |
|---|---|---|
| Admin cannot query | `App.jsx` & `require_student` | Bounced to Admin Dashboard / `403` |
| FastEmbed Confidence | `decision/engine.py` | `approved` / `refused` + Score metric |
| LLM Cannot Guess | `llm/provider.py` | Prompt strictly forbids outside knowledge |
| Document must exist | `get_document_by_id()` | `404 Not Found` |
| Mode must match doc | `validate_document_access()` | `400 Bad Request` |
| Variance Conflict | `rag/conflict.py` | Engine hard-refuses on score spread > 0.65 |
| All decisions audited | `audit/logger.py` | Appended to PostgreSQL `audit_logs` |

---

## Test Results

The RAG application encompasses an intensive **Pytest Suite** designed to programmatically validate the backend governance bounds across all Phases.

```
Phase 4 — Controlled Retrieval: 31/31 ✅
Phase 5 — Controlled Generation: 31/31 ✅
Phase 6 — Decision Engine: 8/8 ✅
Phase 7 — Audit Compliance: 5/5 ✅
```

---

## License

MIT — see [LICENSE](LICENSE)
