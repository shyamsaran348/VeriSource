from fastapi import HTTPException
from app.rag.embeddings import embed_query
from app.rag.vector_store import get_existing_collection

TOP_K = 8


def retrieve(document_id: str, query: str) -> dict:
    """
    Retrieve top-k relevant chunks from a SINGLE document collection.
    Strictly document-scoped. Never touches other collections.
    """

    if not query or not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    # 🔒 Strict retrieval — raises 404 if collection not found, never auto-creates
    collection = get_existing_collection(document_id)

    count = collection.count()
    if count == 0:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    # Embed query using fastembed (ONNX Runtime — no mutex conflict)
    query_embedding = embed_query(query)

    # Query the collection with metadata and distances
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(TOP_K, count),
        include=["documents", "metadatas", "distances"],
    )

    return results