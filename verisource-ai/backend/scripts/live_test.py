# scripts/live_test.py

import sys
import os
import time

from dotenv import load_dotenv

# Add the root backend directory to sys.path regardless of where the script is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(BACKEND_DIR)

# Load environment variables
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

# 🔒 ENVIRONMENT ISOLATION
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

from app.rag.retriever import retrieve
from app.rag.evidence import extract_evidence
from app.rag.conflict import detect_conflict
from app.decision.engine import make_decision
from app.llm.provider import generate_answer
from app.rag.vector_store import init_client
from app.rag.embeddings import get_embedding_model

def run_live_query(document_id: str, query: str, mode: str = "policy"):
    print(f"\n🚀 [REAL-TIME QUERY]")
    print(f"Target Doc: {document_id}")
    print(f"Query: '{query}'")
    print(f"Mode: {mode}")
    print("-" * 40)

    # 1. Retrieval
    print("[1/4] Retrieving from ChromaDB...")
    try:
        raw_results = retrieve(document_id, query, mode)
        print(f"DEBUG: Retrieved {len(raw_results.get('documents', [[]])[0])} chunks.")
        print(f"DEBUG: Top Distances: {raw_results.get('distances', [[]])[0][:3]}")
    except Exception as e:
        print(f"Error during retrieval: {e}")
        # Debugging collections
        import chromadb
        v_path = os.path.join(BACKEND_DIR, "vector_store")
        client = chromadb.PersistentClient(path=v_path)
        print(f"Vector Path: {v_path}")
        print(f"Target: doc_{document_id}")
        print(f"Available: {[c.name for c in client.list_collections()]}")
        raise e
    
    # 2. Evidence Processing
    print("[2/4] Processing Evidence & Stability...")
    evidence_dicts = extract_evidence(raw_results, query)
    conflict = detect_conflict(evidence_dicts, mode)
    similarities = [e['similarity'] for e in evidence_dicts]
    
    # 3. Governance Decision
    print("[3/4] Running Formalized Governance Engine...")
    decision = make_decision(
        mode=mode,
        query_str=query,
        similarities=similarities,
        conflict_flag=conflict,
        model_flag_insufficient=False
    )
    
    print(f"\nDecision: {decision['decision'].upper()}")
    print(f"Confidence: {decision['confidence_score']}")
    print(f"Governance Reason: {decision['reason']}")

    if decision['decision'] == "approved":
        # 4. LLM Synthesis
        print("\n[4/4] Synthesis: Invoking Groq (Llama-3.1)...")
        evidence_texts = [e['text'] for e in evidence_dicts]
        answer = generate_answer(mode, query, evidence_texts)
        print("\n=== SYSTEM ANSWER ===")
        print(answer)
        print("======================\n")
    else:
        print("\n[!] Refusal Triggered. No LLM synthesis performed.")
        if decision.get('explanation'):
            print(f"Counterfactual Guidance: {decision['explanation'].get('missing_evidence_requirements', [])}")

def main():
    # Warm up
    print("Warming up ML Engine (ONNX)...")
    init_client()
    get_embedding_model()
    
    # Target document from DB
    DOC_ID = "d04c8f3f-b389-4a67-b165-6450623c7fd8" # Audit Test Fresh
    
    # Run a few test cases
    run_live_query(DOC_ID, "What is the tuition fee?", "research")
    time.sleep(1)

    run_live_query(DOC_ID, "What is the training methodology?", "research")
    time.sleep(1)
    
    run_live_query(DOC_ID, "How do we handle weekend parking for interns?", "policy") # Should be refused
    time.sleep(1)

    run_live_query(DOC_ID, "Summarize the key takeaways regarding research ethics.", "research")

if __name__ == "__main__":
    main()
