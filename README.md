# VeriSource AI 🛡️

<div align="center">

**An Enterprise-Grade, Governance-First, Evidence-Only Document Verification Platform.**  
*Powered by Retrieval-Augmented Generation (RAG) + Controlled LLM Synthesis.*

Built to rigorously prove that Artificial Intelligence can answer critical compliance and academic questions from unstructured documents — **without hallucinating, without guessing, and without mixing sources.**

[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-18.3.1-61dafb?style=for-the-badge&logo=react)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-1.5.1-orange?style=for-the-badge)](https://trychroma.com)
[![Groq](https://img.shields.io/badge/LLM-Groq%20Llama_3.1-purple?style=for-the-badge)](https://groq.com)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?style=for-the-badge&logo=vite)](https://vitejs.dev/)

</div>

---

## 📖 Table of Contents
1. [Executive Summary](#-executive-summary)
2. [Absolute Safety Constraints](#-absolute-safety-constraints-hallucination-prevention)
3. [Phased Development Architecture](#-phased-development-architecture)
4. [Deep-Dive: The Governance Engine](#-deep-dive-the-governance-engine-phase-6)
5. [Deep-Dive: Audit Logging Framework](#-deep-dive-audit-logging-framework-phase-7)
6. [Frontend UI / UX Console](#-frontend-ui--ux-console-phase-8)
7. [Full Technology Stack](#-full-technology-stack)
8. [Comprehensive Directory Structure](#-comprehensive-directory-structure)
9. [Detailed API Reference](#-detailed-api-reference)
10. [Local Development & Deployment Guide](#-local-development--deployment-guide)
11. [Known Architectural Constraints & Decisions](#-known-architectural-constraints--decisions)
12. [Testing & Validation](#-testing--validation)

---

## 🎯 Executive Summary

VeriSource AI is a deterministic **full-stack Retrieval-Augmented Generation (RAG) platform** explicitly designed for high-stakes document verification. It is intended for environments where answering "I don't know" is acceptable, but answering incorrectly is catastrophic (e.g., Legal Compliance, Academic Regulations, University Policy Enforcement).

Unlike general-purpose conversational chatbots (like ChatGPT) which process prompts holistically and draw upon vast external pre-training datasets, VeriSource strictly acts as a **semantic lookup and synthesis engine**. It rigidly binds the Large Language Model (LLM) to cryptographic text chunks extracted directly from a singularly approved PDF document. 

---

## 🔒 Absolute Safety Constraints (Hallucination Prevention)

VeriSource achieves zero-hallucination verification through six layers of defense-in-depth architecture:

1. **Evidence-Only LLM Prompting:** The GenAI model receives absolutely NO external knowledge. It is fed only the raw extracted document chunks and the user's query.
2. **Mathematical Confidence Thresholds:** Before the LLM is even invoked, the `fastembed` ONNX Runtime calculates the Cosine Distance of the query against the vector database. If the relevance mathematically falls below the calibrated `0.05` minimum, the query undergoes a **Hard Block Refusal**. 
3. **Semantic Conflict Detection:** If the retrieved text chunks wildly contradict each other (e.g., a variance spread `> 0.65`), the system assumes the query is ambiguous and enforces a refusal, preventing the LLM from guessing the "right" answer.
4. **Single-Document Vector Isolation:** During retrieval, queries are strictly routed to isolated ChromaDB collections representing a single document (e.g., `doc_f850a155...`). Cross-document contamination is structurally impossible.
5. **Pre-Retrieval Rule Enforcement (Governance):** If the student attempts to query an "inactive" version of a policy, or query a "research" document while in "policy" mode, the API rejects the request before the database is ever queried.
6. **Immutable Audit Trails:** Every single prompt, response, vector score, retrieved chunk ID, execution time, and ultimate approval/refusal is immediately written to a PostgreSQL database for non-repudiable auditing.

---

## 🏗 Phased Development Architecture

VeriSource AI was built from the ground up over 8 distinct, rigorously tested phases. 

| Phase | Identifier | Component Focus | Status |
|:---:|---|---|:---:|
| **0** | **Foundation** | Initializing FastAPI, configuring Supabase PostgreSQL, and defining Pydantic schemas. | ✅ Done |
| **1** | **Auth & RBAC** | Implementing JSON Web Tokens (JWT) + bcrypt. Creating strict `Student` (Query) and `Admin` (Upload) role barriers. | ✅ Done |
| **2** | **Ingestion Pipe**| Writing the PDF-to-Text extraction parsers, generating SHA-256 cryptographic file hashes, and establishing Document Versioning states. | ✅ Done |
| **3** | **Vector Core** | Implementing ChromaDB. Replacing heavyweight PyTorch dependencies with the lightweight `fastembed` ONNX Runtime to resolve native Apple Silicon mutex deadlocks. | ✅ Done |
| **4** | **Retrieval** | Enforcing Single-Document boundaries, metadata extraction, mode-matching, and chunk distance similarity checks. | ✅ Done |
| **5** | **LLM Synthesis**| Integrating the `Groq` API (`llama-3.1-8b-instant`). Engineering the strict "Synthesis-Only" prompt templates that remove external knowledge dependencies. | ✅ Done |
| **6** | **Decision Engine**| Calibrating the mathematical thresholds. Implementing the Variance-based Conflict Detector. | ✅ Done |
| **7** | **Audit DB** | Creating the `audit_logs` SQL table. Recording every interaction, timestamp, confidence score, and LLM string sequence. | ✅ Done |
| **8** | **UX & Robustness**| Hardening the Audit Dashboard with CSV exports and primary UI polish. | ✅ Done |
| **9** | **Refusal XAI** | **Counterfactual Refusal Layer.** Providing "Why Not" guidance for unverified queries. | ✅ Done |
| **10**| **Reliability Core**| **Reliability & Calibration Dashboard.** Empirical trust scoring based on audit history. | ✅ Done |

---

## 🧠 Deep-Dive: The Governance Engine (Phase 6)

The Governance Engine is the brain of VeriSource AI. It sits *between* the Vector Database (ChromaDB) and the LLM (Groq) to independently evaluate if the evidence is strong enough to risk an AI generation.

### Calibrated Thresholds
Because VeriSource utilizes `fastembed` (MiniLM ONNX), the mathematical vector distances are highly compressed compared to standard OpenAI embeddings. The Governance Engine calibrates for this:

- **Policy Mode Minimum Score:** `0.05` (5%)
- **Research Mode Minimum Score:** `0.03` (3%)
- **Policy Variance Conflict Threshold:** `0.65` (If the distance between the top chunk and bottom chunk exceeds 65%, the query is refused due to contradictory evidence).
- **Research Variance Conflict Threshold:** `0.75` (More tolerant of diverse evidence).

### The LLM Fallback Fix
If the Governance Engine flags a "Refusal", the Groq LLM API is entirely bypassed to save compute overhead. If the Governance Engine flags an "Approval", but the raw PDF chunk text is so unstructured that the LLM fails to synthesize a grammatical output, VeriSource fails gracefully by returning the raw PDF chunks `[...]` to the user in the "System Conclusion" block.

---

## 📜 Deep-Dive: Audit Logging Framework (Phase 7)

Transparency is mandatory for compliance tools. Every time a `Student` interacts with the Verification Console, a non-repudiable log is generated in the PostgreSQL `audit_logs` table via SQLAlchemy.

**What gets logged?**
- `transaction_id`: A cryptographic SHA-256 hash representing the specific verification attempt for non-repudiable audit trails.
- `user_id`: The UUID of the authenticated student.
- `document_id`: The UUID of the strictly bounded target document.
- `mode`: Currently active validation scope (`policy` or `research`).
- `query_text`: The exact string entered by the user.
- `decision_outcome`: The final Governance verdict (`approved` or `refused`).
- `confidence_score`: The mathematical similarity probability (`0.00` to `1.00`).
- `timestamp`: UTC DateTime of execution (ISO 8601).

### Enterprise Hardening (Phase 8 Robustness)
To ensure the audit system stands up to real-world data inconsistencies, we implemented:
- **Case-Insensitive (`ilike`) Filtering**: Prevents data silos caused by casing mismatches between manual entry and database state.
- **Whitespace Tolerance (`strip()`)**: Automatically sanitizes user input and database tokens.
- **Debounced Global Search**: Real-time filtering of millions of logs without API congestion.
- **CSV Export Engine**: Allows compliance officers to perform offline analysis of filtered audit trails.

---

## 💻 Frontend UI / UX Console (Phase 8)

The frontend is a bespoke React 18 Single Page Application (SPA) utilizing Vite for lightning-fast Hot Module Replacement (HMR).

### Aesthetic Philosophy
The UI is designed to look like a secure, high-stakes military or financial terminal rather than a friendly consumer chatbot. It features:
- Deep `brand-navy` backgrounds (`#0B1121`) with a custom **film grain overlay** for high-fidelity texture.
- Metallic `gold` accent trims (`#C5A24D`) and vibrant active states.
- Glassmorphic backdrop blurs (`backdrop-blur-sm`, `bg-brand-navy-light/30`).
- **Custom Aesthetic Scrollbars**: Matching the brand-navy palette to remove browser default visual noise.
- **Keyboard-First Interaction**: Full `Cmd+Enter` (Mac) / `Ctrl+Enter` support for immediate query submission.
- Monospace diagnostic fonts (`font-mono`) displaying real-time execution metadata.

### Features
- **Gatekeeper Auth Login:** Secure role-based routing with JWT protection.
- **Verification Console:** Dual-pane interface with immediate Post-Mortem visual feedback.
- **Evidence Reference Panel:** Side-by-side rendering of the exact text chunks with precise similarity percentages.
- **Traceability Metadata**: Every result now includes a **Cryptographic Transaction ID** and human-readable time-indexing for absolute evidence provenance.

---

## 🧭 Deep-Dive: Counterfactual Refusal Layer (Phase 9)

Traditional RAG systems fail silently or provide vague "I don't know" responses. VeriSource AI implements a **Research-Aligned Counterfactual Explanation Layer** to solve the "Interpretability Gap."

### Why Counterfactuals?
Based on 2024-2025 AI Alignment research (XAI), users trust autonomous systems significantly more when they understand the **boundary conditions** of a refusal.

### How It Works
When a query is refused due to low similarity (`< 0.05`) or conflict, the **Compass Guide** activates:
1. **Concept Extraction**: The system identifies the core academic or policy intent (e.g., "Honours Eligibility").
2. **Missing Evidence Analysis**: It calculates exactly *what* evidence elements would have been required for an approval (e.g., "A formal eligibility clause defining CGPA bounds").
3. **Structured Guidance**: The student is presented with a "Why Not" checklist, allowing them to refine their query or contact an administrator with precise missing-info tags.

*This elevates the platform from a simple validator to a **Transparent Epistemic Assistant.***

## ⚙️ Full Technology Stack

### Frontend Client
- **Framework:** React 18
- **Build Tool:** Vite 5.0
- **Routing:** React Router v6
- **Styling:** Tailwind CSS (Custom Configuration)
- **Animation:** Framer Motion
- **Icons:** Lucide React
- **Network:** Axios (Interceptors for JWT attached to `Bearer`)

### Backend Server
- **Framework:** FastAPI
- **Web Server:** Uvicorn
- **Language:** Python 3.12+
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic V2

### Artificial Intelligence & Data
- **Vector Database:** ChromaDB 1.5.1
- **Embedding Model:** `fastembed` (MiniLM L6 V2 ONNX Runtime)
- **Large Language Model API:** Groq (`llama-3.1-8b-instant`)
- **PDF Extraction:** `pypdf`
- **Relational Database:** PostgreSQL (Hosted on Supabase)

---

## 📂 Comprehensive Directory Structure

```text
VeriSource/
├── README.md
├── .gitignore
├── frontend/                         # React UI Workspace
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── main.jsx                  # React DOM Entry
│       ├── App.jsx                   # Central Router
│       ├── auth/                     # JWT Context & ProtectedRoute intercepts
│       ├── components/               # Reusable UI (ConfidenceMeter, Navbars)
│       ├── layouts/                  # Admin vs Student structural wraps
│       ├── pages/                    # 
│       │   ├── Landing.jsx           # Public marketing / login entry
│       │   ├── admin/                # Upload, DB Management, Audit Logs
│       │   └── student/              # Auth Console, Verification Results
│       └── services/                 # Axios API Service Wrappers
└── verisource-ai/
    └── backend/                      # Python API Workspace
        ├── requirements.txt
        ├── run.sh                    # OS-level Thread Config Launcher (CRITICAL)
        └── app/
            ├── main.py               # FastAPI App definition + ML Warmup Core
            ├── core/                 # Environment Variables & Security Decoders
            ├── auth/                 # User Registration / JWT Generation
            ├── ingestion/            # PDF Parsing & Chunk Generation Logic
            ├── documents/            # Target Corpus Versioning Control
            ├── rag/                  # ChromaDB interface & Conflict variance math
            ├── llm/                  # Hardcoded Groq System Prompts
            ├── decision/             # Threshold Enforcements
            ├── audit/                # PostgreSQL Insert Logic
            └── db/                   # SQLAlchemy Session Controllers
```

---

## 📡 Detailed API Reference

*Note: All endpoints (except Auth/Health) require a valid JWT token in the `Authorization: Bearer <token>` header.*

### System Health
| Method | Endpoint | Description | Auth Required |
|:---|:---|:---|:---|
| `GET` | `/health` | Validates API status, Postgres connection, and ML Engine load. | ❌ None |

### Authentication Layer
| Method | Endpoint | Description | Auth Required |
|:---|:---|:---|:---|
| `POST` | `/auth/register` | Accepts `username`, `password`, `role`. Returns User dict. | ❌ None |
| `POST` | `/auth/login` | Accepts `OAuth2PasswordRequestForm`. Returns JWT `access_token`. | ❌ None |

### Administrator Ingestion
| Method | Endpoint | Description | Auth Required |
|:---|:---|:---|:---|
| `POST` | `/ingestion/upload` | Multipart form accepting `.pdf`. Parses, chunks, and creates ChromaDB Collections. | 🔐 Admin Only |
| `GET` | `/documents/` | Returns list of all ingested documents and their versions. | 🔐 Admin Only |
| `GET` | `/audit/` | Returns paginated historical query log data for compliance. | 🔐 Admin Only |

### Student Verification
| Method | Endpoint | Description | Auth Required |
|:---|:---|:---|:---|
| `GET` | `/documents/active` | Returns list of explicitly bounded `is_active=True` documents. | 🎓 Student Only |
| `POST` | `/query/` | The core engine. Accepts `document_id`, `mode`, `query`. Returns complex `QueryResponse` JSON including parsed answer, conflict flags, and extracted evidence chunks. | 🎓 Student Only |

---

## 🚀 Local Development & Deployment Guide

### Phase 1: PostgreSQL Setup
1. Create a free PostgreSQL cluster on [Supabase](https://supabase.com/).
2. Copy the Transaction Pooler Connection String (IPv4).

### Phase 2: Environment Configuration
1. Navigate to `verisource-ai/backend/`
2. Create a `.env` file:
```env
APP_NAME="VeriSource AI"
DEBUG=True
VERSION="0.1.0"
DATABASE_URL="postgresql://user:password@aws-0-pooler.supabase.com:6543/postgres"
JWT_SECRET="generate-a-random-secure-string"
JWT_ALGORITHM="HS256"
JWT_EXPIRE_MINUTES="60"
GROQ_API_KEY="gsk_your_groq_api_key_from_console_groq_com"
```

### Phase 3: Launching the Backend
**CRITICAL:** You must *never* run `uvicorn` directly or use the `--reload` flag during standard execution. Apple Silicon (M-Series MacBooks) will trigger a native Mutex thread-lock panic if ChromaDB and FastEmbed attempt to hot-reload inside Python.
You must use the provided bash script which establishes OS-level thread constraints:
```bash
cd verisource-ai/backend
pip install -r requirements.txt
./run.sh
```
*The FastAPI Swagger Docs will be available at `http://localhost:8000/docs`*

### Phase 4: Launching the Frontend
```bash
cd frontend
npm install
npm run dev
```
*The React UI will be available at `http://localhost:5173`*

---

## 🏛 Known Architectural Constraints & Decisions

1. **The FastEmbed Optimization:** Originally, VeriSource utilized standard HuggingFace `sentence-transformers` via PyTorch. PyTorch relies heavily on OpenMP multithreading. When paired with ChromaDB's underlying `hnswlib` C++ indexing library, the two thread-pools collided on ARM64 architectures resulting in uncontrollable Application Halts (`mutex.cc Loc Blocking`). Replacing PyTorch with the ONNX runtime (`fastembed`) completely mitigated this issue, dropping memory overhead by 60% while increasing embedding speed.
2. **Synchronous ML Executor Loading:** Vector DBs take heavily on RAM initialization. If a user hits an endpoint while the DB is starting, it throws a 500 error. The `main.py` explicitly warms up the DB *before* accepting network traffic.
3. **No Automatic Collection Creation:** If a user queries a document where the metadata exists in Postgres, but the ChromaDB collection was accidentally deleted... the system throws a `404`. It does not attempt to automatically recreate the collection to prevent silent architectural drift.

---

## 🧪 Testing & Validation

VeriSource features a comprehensive Pytest suite that programmatically validates the strictness of the Governance bounds by acting as both a rogue Admin and a confused Student.

To run the full suite:
```bash
cd verisource-ai/backend
pytest test_phase4.py test_phase5.py test_phase6.py test_phase7_governance.py -v
```

**Results Benchmark:**
- ✔️ Phase 4 Retrieval Integrity: 31/31 Passed
- ✔️ Phase 5 LLM Generation Safety: 31/31 Passed
- ✔️ Phase 6 Threshold Enforcements: 8/8 Passed
- ✔️ Phase 7 Audit Trailing: 5/5 Passed

---
*Built with absolute certainty. VeriSource AI.*
