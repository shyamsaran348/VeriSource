import asyncio
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.core.logging import get_logger
from app.db.session import get_db
from app.documents.service import create_document
from app.ingestion.hasher import generate_sha256

logger = get_logger()
router = APIRouter(prefix="/ingestion", tags=["Ingestion"])

UPLOAD_DIR = Path("uploaded_files")
UPLOAD_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Pure CPU helpers — imported & called only inside thread pool
# ---------------------------------------------------------------------------

def _run_pipeline(file_path: str, document_id: str):
    """
    Synchronous ingestion pipeline: parse → chunk → embed → store.
    Runs in a thread pool; must NOT touch the event loop.
    Returns number of chunks created on success; raises on error.
    """
    from app.ingestion.parser import extract_text_from_pdf
    from app.rag.chunker import chunk_text
    from app.rag.embeddings import embed_texts
    from app.rag.vector_store import add_document_chunks

    # 1️⃣ Parse
    logger.info("Extracting text from PDF...")
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise ValueError("Document contains no extractable text")

    # 2️⃣ Chunk
    logger.info("Chunking text...")
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("Document could not be chunked")
    logger.info(f"Created {len(chunks)} chunks.")

    # 3️⃣ Embed
    logger.info("Embedding chunks...")
    embeddings = embed_texts(chunks)
    logger.info(f"Generated {len(embeddings)} embeddings.")

    # 4️⃣ Store
    logger.info("Writing to vector store...")
    add_document_chunks(
        document_id=document_id,
        chunks=chunks,
        embeddings=embeddings,
    )
    logger.info("Vector store write complete.")

    return len(chunks)


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/upload")
async def upload_document(
    name: str = Form(...),
    mode: str = Form(...),
    version: str = Form(...),
    authority: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    if mode not in ["policy", "research"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Must be 'policy' or 'research'.")

    logger.info(f"Ingestion request: file={file.filename} mode={mode}")

    # ── I/O: read & save file (async-safe) ──────────────────────────────────
    file_bytes = await file.read()
    file_hash = generate_sha256(file_bytes)

    ext = (file.filename or "bin").rsplit(".", 1)[-1]
    unique_filename = f"{uuid.uuid4()}.{ext}"
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as fh:
        fh.write(file_bytes)

    logger.info(f"Saved {file.filename} → {file_path}  sha256={file_hash[:12]}…")

    # ── DB: create document record (flush only) ──────────────────────────────
    try:
        document = create_document(
            db=db,
            name=name,
            mode=mode,
            version=version,
            authority=authority,
            file_hash=file_hash,
        )
        logger.info(f"Document record created: id={document.document_id}")
    except Exception as e:
        logger.error(f"DB record creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    # ── CPU pipeline: run on shared ML_EXECUTOR (single named thread)
    # Using the same thread as startup warm-up — zero mutex races with
    # hnswlib or PyTorch since they share one native thread context.
    try:
        from app.main import ML_EXECUTOR
        loop = asyncio.get_event_loop()
        chunks_created = await loop.run_in_executor(
            ML_EXECUTOR,
            _run_pipeline,
            str(file_path),
            str(document.document_id),
        )
    except ValueError as e:
        # Expected validation errors (no text, no chunks)
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ingestion pipeline error: {e}")

    # ── Commit only after successful indexing ────────────────────────────────
    db.commit()
    db.refresh(document)
    logger.info("Ingestion complete.")

    return {
        "document_id": document.document_id,
        "message": "Document uploaded and indexed successfully",
        "chunks_created": chunks_created,
    }