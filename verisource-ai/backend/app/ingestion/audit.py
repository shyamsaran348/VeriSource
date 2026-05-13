import random
import asyncio
from sqlalchemy.orm import Session
from app.documents.models import Document
from app.rag.vector_store import get_existing_collection
from app.rag.embeddings import embed_query
from app.rag.retriever import retrieve
from app.rag.evidence import extract_evidence
from app.decision.engine import make_decision
from app.core.logging import get_logger

logger = get_logger()

# ── AUDIT PROMPTS ─────────────────────────────────────────────────────────────

AUDIT_GENERATION_PROMPT = """You are a regulatory auditor. 
Given the following excerpts from a document, generate exactly 3 highly specific technical questions that MUST be answered using ONLY these excerpts.
Focus on dates, numbers, requirements, or specific names.

Excerpts:
{excerpts}

Questions:
1."""

def _generate_questions(excerpts: list[str]) -> list[str]:
    """Uses LLM to generate stress-test questions from document chunks."""
    from app.llm.provider import _get_groq_client
    
    combined_excerpts = "\n\n---\n\n".join(excerpts)
    client = _get_groq_client()
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Generate specific verification questions based on text."},
            {"role": "user", "content": AUDIT_GENERATION_PROMPT.format(excerpts=combined_excerpts)},
        ],
        temperature=0.3,
        max_tokens=256,
    )
    
    raw = response.choices[0].message.content
    # Simple split-by-line parsing
    lines = [line.strip() for line in raw.split("\n") if line.strip() and ("?" in line or line[0].isdigit())]
    return lines[:3]

async def run_document_audit(db: Session, document: Document):
    """
    Meta-RAG: Audit document quality and reliability.
    """
    logger.info(f"Starting Quality Audit for document: {document.name} (ID: {document.document_id})")
    
    try:
        # 1. Get sample chunks for question generation
        collection = get_existing_collection(str(document.document_id))
        count = collection.count()
        if count == 0:
            return None
            
        sample_indices = random.sample(range(count), min(5, count))
        # Fetching by index is not direct in Chroma, so we fetch all and slice
        all_chunks = collection.get(include=["documents"])["documents"]
        samples = [all_chunks[i] for i in sample_indices]
        
        # 2. Generate Stress Test Questions
        # We run this in a thread because it's a blocking LLM call
        questions = await asyncio.to_thread(_generate_questions, samples)
        logger.info(f"Generated {len(questions)} stress-test questions.")
        
        # 3. Perform Internal Verification Loop
        audit_score = 0
        coverage_results = []
        
        for q in questions:
            # Strip numbering if present
            clean_q = q.split(".", 1)[-1].strip() if "." in q[:3] else q
            
            # Simulated Retrieval
            raw_results = retrieve(str(document.document_id), clean_q, document.mode)
            evidence_dicts = extract_evidence(raw_results, clean_q)
            similarities = [e["similarity"] for e in evidence_dicts]
            
            # Run Decision Engine
            decision = make_decision(
                mode=document.mode,
                query_str=clean_q,
                similarities=similarities,
                conflict_flag=False, # Initial check
                model_flag_insufficient=False
            )
            
            status = "pass" if decision["decision"] == "approved" else "fail"
            score = decision["confidence_score"]
            audit_score += score
            
            coverage_results.append({
                "question": clean_q,
                "status": status,
                "confidence": score
            })
            
        final_score = (audit_score / len(questions)) if questions else 0
        
        # 4. Final Audit Metrics
        results = {
            "overall_reliability": round(final_score * 100, 1),
            "clarity_rating": "High" if final_score > 0.7 else "Medium" if final_score > 0.4 else "Low",
            "coverage_gap_detected": any(r["status"] == "fail" for r in coverage_results),
            "stress_tests": coverage_results,
            "audit_timestamp": document.created_at.isoformat() if document.created_at else None
        }
        
        # Save to DB
        document.audit_results = results
        db.add(document)
        db.commit()
        
        logger.info(f"Quality Audit complete. Score: {results['overall_reliability']}%")
        return results

    except Exception as e:
        logger.error(f"Quality Audit failed: {e}")
        return None
