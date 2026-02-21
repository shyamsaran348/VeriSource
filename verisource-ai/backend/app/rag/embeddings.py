"""
Embedding module — uses fastembed (ONNX Runtime based).

Safe for Apple Silicon + Chroma HNSW.
No OpenMP conflicts.
384-dimensional MiniLM output.
"""

from functools import lru_cache
from fastembed import TextEmbedding

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> TextEmbedding:
    return TextEmbedding(model_name=MODEL_NAME)


# ==============================
# INGESTION (Batch)
# ==============================

def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    embeddings = list(model.embed(texts))
    return [e.tolist() for e in embeddings]


# ==============================
# RETRIEVAL (Single Query)
# ==============================

def embed_query(query: str) -> list[float]:
    model = get_embedding_model()
    embedding = next(model.embed([query]))
    return embedding.tolist()