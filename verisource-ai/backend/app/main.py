# app/main.py

import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import get_logger
from app.users.models import User
from app.documents.models import Document
from app.audit.models import AuditLog
from app.db.base import Base
from app.db.session import engine

# Import all routers
from app.auth.router import router as auth_router
from app.ingestion.router import router as ingestion_router
from app.documents.router import router as documents_router
from app.query.router import router as query_router
from app.audit.router import router as audit_router

# Initialize the global logger
logger = get_logger()

# 🔒 ENVIRONMENT ISOLATION: Must be set BEFORE native C++ imports (torch/hnswlib).
# This prevents race conditions in the underlying BLAS/OpenMP libraries.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

# 🔑 SINGLE-THREAD ML EXECUTOR:
# All calls to ChromaDB, HNSWlib, or PyTorch are routed through this executor.
# This strictly enforces serialized execution to prevent native-mutex contention 
# which is a common cause of "RAW: Lock blocking" crashes on ARM architectures (Apple Silicon).
ML_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ml-worker")

# Initialize FastAPI Application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Institutional-grade RAG governance platform with strict evidence gating."
)

# CORS Policy: Restricted origins should be configured for production deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route Registration
app.include_router(auth_router)
app.include_router(ingestion_router)
app.include_router(documents_router)
app.include_router(query_router)
app.include_router(audit_router)

def _startup_warmup():
    """
    Initializes heavy ML models and vector clients in the background.
    Runs on the dedicated ML_EXECUTOR thread to avoid blocking the main loop.
    """
    from app.rag.vector_store import init_client
    init_client()

    from app.rag.embeddings import get_embedding_model
    get_embedding_model() # Trigger model download and ONNX loading

@app.on_event("startup")
async def startup_event():
    """
    FastAPI startup hook. Ensures DB schema and warms up the AI engine.
    """
    logger.info("===================================")
    logger.info(f"VeriSource AI Backend: {settings.APP_NAME} v{settings.VERSION}")
    logger.info("===================================")

    # Automatically create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database engine initialized.")

    # Warm up ML models in the background
    logger.info("Warming up ML context on dedicated thread...")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(ML_EXECUTOR, _startup_warmup)
    logger.info("System Ready.")

@app.get("/health")
async def health_check():
    """
    Service health check for monitoring and orchestrators.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "mode": "production_stable"
    }