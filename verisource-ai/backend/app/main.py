import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

# 🔒 Must be set BEFORE any C extension (torch/hnswlib/chromadb) is imported.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import get_logger

from app.users.models import User          # noqa: F401
from app.documents.models import Document  # noqa: F401
from app.audit.models import AuditLog  # noqa: F401

from app.db.base import Base
from app.db.session import engine

from app.auth.router import router as auth_router
from app.ingestion.router import router as ingestion_router
from app.documents.router import router as documents_router
from app.query.router import router as query_router
from app.audit.router import router as audit_router

logger = get_logger()

# ─────────────────────────────────────────────────────────────────────────────
# 🔑 SINGLE-THREAD EXECUTOR
#
# All calls that touch native C++ libraries (chromadb/hnswlib, PyTorch/OpenMP)
# must run on THIS executor — serialised to ONE thread. This prevents any
# concurrent native-mutex contention between PyTorch thread pools and
# hnswlib's abseil mutex, which produces:
#
#     [mutex.cc : 452] RAW: Lock blocking
#
# The executor is created here at module scope so the same thread is reused
# for both startup warm-up and every ingestion request.
# ─────────────────────────────────────────────────────────────────────────────
ML_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ml-worker")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(ingestion_router)
app.include_router(documents_router)
app.include_router(query_router)
app.include_router(audit_router)


def _startup_warmup():
    """
    Runs in the dedicated ML thread.
    Initialises ChromaDB then PyTorch sequentially — same thread, no races.
    """
    from app.rag.vector_store import init_client
    init_client()

    from app.rag.embeddings import get_embedding_model
    get_embedding_model()  # downloads & caches model on first call


@app.on_event("startup")
async def startup_event():
    logger.info("===================================")
    logger.info("VeriSource AI Backend Starting...")
    logger.info(f"App Name: {settings.APP_NAME}")
    logger.info(f"Version: {settings.VERSION}")
    logger.info("===================================")

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured.")

    logger.info("Warming up vector store + embedding model on dedicated ML thread...")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(ML_EXECUTOR, _startup_warmup)
    logger.info("ML warm-up complete. Application ready.")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
    }