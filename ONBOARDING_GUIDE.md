# 🚀 VeriSource AI: Developer Onboarding Guide

Welcome to the VeriSource AI project! 

This guide is designed to help you quickly understand the project architecture, spin up the local environment, and start contributing.

---

## 🎯 What is VeriSource AI?
VeriSource AI is **not** a standard chatbot. It is a highly constrained, enterprise-grade **Document Verification Platform**. It uses Retrieval-Augmented Generation (RAG) to read unstructured PDFs (like University Policies or Research Papers) and strictly limits the Large Language Model (LLM) to *only* answer based on retrieved evidence.

If the evidence is missing or contradictory, VeriSource mathematically blocks the AI from answering, preventing hallucinations.

---

## 🏗️ Where is everything? (Architecture Map)

The project is split into two independent workspaces.

### 1. The React Frontend (`/frontend`)
A Vite + React 18 single-page application designed with a high-fidelity "glassmorphic terminal" aesthetic.
- **Key Location:** `frontend/src/components/` (Look for `DecisionCard.jsx` and `TrustDiagnostics.jsx` to see how we render the mathematical governance metrics).
- **Styling:** TailwindCSS + Framer Motion.

### 2. The FastAPI Backend (`/verisource-ai/backend`)
The core Python engine that handles embeddings, vector storage, and deterministic governance.
- **`app/main.py`**: The API Gateway and entry point.
- **`app/decision/engine.py`**: 🧠 **The Brain of the System.** This is the "Governance Engine" that evaluates Shannon Entropy and Standard Deviation to decide if an answer is safe to generate.
- **`app/rag/vector_store.py`**: Handles ChromaDB and the ONNX FastEmbed local ML models.
- **`scripts/`**: Contains our `eval_dataset.json` and `reliability_benchmark.py` which mathematically prove the system works.

*(For a full deep-dive, see `SYSTEM_ARCHITECTURE.md` and `README.md`)*.

---

## ⚙️ Quickstart Setup

You will need two API keys before you begin:
1. **Groq API Key**: (For lightning-fast Llama-3.1 inference). Get it free at `console.groq.com`.
2. **Supabase Database URL**: (For PostgreSQL Audit Logs).

### Step 1: Backend Setup
1. Open a terminal and navigate to the backend: `cd verisource-ai/backend`
2. Create a `.env` file in the `backend` folder:
```env
APP_NAME="VeriSource AI"
DEBUG=True
VERSION="0.1.0"
DATABASE_URL="postgresql://user:password@aws-0-pooler.supabase.com:6543/postgres"
JWT_SECRET="your_secret_key"
JWT_ALGORITHM="HS256"
JWT_EXPIRE_MINUTES="60"
GROQ_API_KEY="gsk_your_groq_key"
```
3. Install dependencies: `pip install -r requirements.txt`
4. **CRITICAL:** Do NOT run `uvicorn main:app --reload` on MacBooks! It will cause a thread-lock crash between PyTorch and ChromaDB. Instead, run our custom bash script:
```bash
./run.sh
```
*The API will be live at `http://localhost:8000/docs`*

### Step 2: Frontend Setup
1. Open a new terminal and navigate to the frontend: `cd frontend`
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev`
*The UI will be live at `http://localhost:5173`*

---

## 🧪 Testing the Governance Engine
Want to see the math in action without running the UI? We built a full automated benchmark that simulates retrieval vectors to test the safety bounds.
```bash
cd verisource-ai/backend
python3 scripts/reliability_benchmark.py
```
This runs 50 edge-cases (hallucinations, contradictions, prompt injections) and guarantees a **100% Deterministic Safety Recall**.

---
*Happy coding! Feel free to reach out if you have any questions about the Shannon Entropy thresholds or the ChromaDB structure.*
