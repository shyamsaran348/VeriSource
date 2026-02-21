"""
Audit Router — Phase 7.
Admin-only endpoint to read audit logs.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin, get_db
from app.audit.models import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs")
def get_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Phase 7 — Admin audit log viewer.
    Returns the most recent audit log entries (newest first).
    """
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "document_id": str(log.document_id),
            "mode": log.mode,
            "query_hash": log.query_hash,
            "decision": log.decision,
            "confidence_score": log.confidence_score,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        }
        for log in logs
    ]
