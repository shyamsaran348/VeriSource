# app/rag/evidence.py

from typing import List, Dict
from fastapi import HTTPException
import re

def extract_evidence(results: dict, query: str = "") -> List[Dict]:
    """
    Semantic Evidence Processor: Extracts and scores relevant text fragments.
    
    This function processes raw distance vectors from ChromaDB and applies 
    higher-order logic (like keyword boosting) to improve groundedness.

    Args:
        results: Raw dictionary from ChromaDB .query()
        query: The user's query (used for technical acronym boosting)

    Returns:
        List of structured evidence blocks with technical scores.
    """

    if not results:
        raise HTTPException(status_code=500, detail="Invalid retrieval result structure.")

    # 🚀 TECHNICAL KEYWORD BOOST:
    # Identify technical acronyms (e.g. CBCS, R2021) to prioritize precision matches.
    acronyms = re.findall(r'[A-Z0-9-]{3,}', query)

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    distances = results.get("distances", [])

    if not documents or not documents[0]:
        raise HTTPException(status_code=404, detail="No relevant evidence found.")

    evidence_blocks = []
    docs = documents[0]
    metas = metadatas[0]
    dists = distances[0]

    for doc_text, meta, distance in zip(docs, metas, dists):
        if not meta or "chunk_id" not in meta:
            continue

        # ⚖️ BASE SIMILARITY: 1 - L2 distance (or cosine distance depending on space)
        similarity_score = 1 - distance
        
        # 📈 APPLIED BOOST:
        # If a chunk contains an exact match for a technical acronym in the query,
        # we boost its score to ensure it survives the governance gate.
        boost = 0.0
        for acr in acronyms:
            if acr in doc_text:
                boost = 0.3
                break
        
        final_sim = similarity_score + boost
        
        evidence_blocks.append({
            "chunk_id": meta["chunk_id"],
            "text": doc_text,
            "similarity": round(final_sim, 4)
        })

    return evidence_blocks