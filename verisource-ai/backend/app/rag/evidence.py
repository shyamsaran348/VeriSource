from typing import List, Dict
from fastapi import HTTPException


def extract_evidence(results: dict) -> List[Dict]:
    """
    Convert raw Chroma query results into structured evidence blocks.

    Enforces:
    - At least one result must exist
    - Metadata must include chunk_id
    - Converts distance -> similarity score
    """

    if not results:
        raise HTTPException(
            status_code=500,
            detail="Invalid retrieval result structure."
        )

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    distances = results.get("distances", [])

    # Chroma returns nested lists
    if not documents or not documents[0]:
        raise HTTPException(
            status_code=404,
            detail="No relevant evidence found in selected document."
        )

    evidence_blocks = []

    docs = documents[0]
    metas = metadatas[0]
    dists = distances[0]

    for doc_text, meta, distance in zip(docs, metas, dists):

        if not meta or "chunk_id" not in meta:
            raise HTTPException(
                status_code=500,
                detail="Chunk metadata missing chunk_id."
            )

        similarity_score = 1 - distance  # Convert cosine distance → similarity

        evidence_blocks.append({
            "chunk_id": meta["chunk_id"],
            "text": doc_text,
            "score": round(similarity_score, 4)
        })

    return evidence_blocks