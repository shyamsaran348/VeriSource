import hashlib
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.audit.models import AuditLog
from app.core.logging import get_logger

logger = get_logger()


def hash_query(query: str) -> str:
    return hashlib.sha256(query.encode("utf-8")).hexdigest()


def log_query_interaction(
    db: Session,
    user_id: int,
    document_id,
    mode: str,
    query: str,
    decision: str,
    confidence_score: float,
    conflict_detected: bool = False,
):
    """
    Phase 7 — Safe Audit Logging
    (Phase 10 Update: Added conflict_detected)

    - Hashes query (never stores raw text)
    - Logs approved and refused
    - Does NOT crash query flow if logging fails
    - Rolls back safely on error
    """

    try:
        query_hash = hash_query(query)

        log_entry = AuditLog(
            user_id=user_id,
            document_id=document_id,
            mode=mode,
            query_hash=query_hash,
            decision=decision,
            confidence_score=confidence_score,
            conflict_detected=conflict_detected,
        )

        db.add(log_entry)
        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Audit logging failed: {str(e)}")