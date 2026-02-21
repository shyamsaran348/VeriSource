import chromadb
from pathlib import Path
from fastapi import HTTPException

VECTOR_PATH = Path("vector_store")
_client = None


def init_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        VECTOR_PATH.mkdir(exist_ok=True)
        _client = chromadb.PersistentClient(path=str(VECTOR_PATH))
    return _client


def get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        return init_client()
    return _client


# ==============================
# INGESTION COLLECTION ACCESS
# ==============================

def get_or_create_collection(document_id: str):
    """
    Used ONLY during ingestion.
    Safe to create.
    """
    collection_name = f"doc_{document_id}"
    return get_client().get_or_create_collection(name=collection_name)


# ==============================
# RETRIEVAL COLLECTION ACCESS
# ==============================

def get_existing_collection(document_id: str):
    """
    Used ONLY during retrieval.
    MUST NOT create new collection.
    """
    collection_name = f"doc_{document_id}"

    collections = [c.name for c in get_client().list_collections()]
    if collection_name not in collections:
        raise HTTPException(
            status_code=404,
            detail="Vector collection not found for this document."
        )

    return get_client().get_collection(name=collection_name)


# ==============================
# ADD CHUNKS (INGESTION)
# ==============================

def add_document_chunks(
    document_id: str,
    chunks: list[str],
    embeddings: list[list[float]],
):
    collection = get_or_create_collection(document_id)

    ids = [f"{document_id}_{i}" for i in range(len(chunks))]

    metadatas = [
        {
            "document_id": document_id,
            "chunk_id": ids[i]
        }
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )