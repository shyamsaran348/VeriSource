"""
Audit Router — Phase 7.
Admin-only endpoint to read audit logs.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin, get_db
from app.audit.models import AuditLog
from app.audit.analytics import get_document_reliability_metrics

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs")
def get_audit_logs(
    mode: str = None,
    decision: str = None,
    query_hash: str = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Phase 7 — Admin audit log viewer with search and filtering support.
    """
    query = db.query(AuditLog)
    
    if mode:
        query = query.filter(AuditLog.mode.ilike(mode.strip()))
    if decision:
        query = query.filter(AuditLog.decision.ilike(decision.strip()))
    if query_hash:
        query = query.filter(AuditLog.query_hash.ilike(f"%{query_hash.strip()}%"))
        
    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

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


@router.get("/reliability")
def get_reliability_analytics(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Phase 10 — Empirical Document Reliability Dashboard
    - Measures how accurately a document performs under governance.
    """
    return get_document_reliability_metrics(db)
