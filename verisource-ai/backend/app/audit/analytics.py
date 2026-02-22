# app/audit/analytics.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.audit.models import AuditLog
from app.documents.models import Document
from typing import List, Dict

def get_document_reliability_metrics(db: Session) -> List[Dict]:
    """
    Computes empirical reliability metrics for all documents based on audit history.
    Aligns with AI Reliability Engineering & Calibration research.
    """
    
    # 1. Group by document_id and aggregate stats
    stats = db.query(
        AuditLog.document_id,
        func.count(AuditLog.id).label("total_queries"),
        func.avg(AuditLog.confidence_score).label("avg_confidence"),
        func.sum(func.cast(AuditLog.decision == "approved", func.Integer)).label("approvals"),
        func.sum(func.cast(AuditLog.conflict_detected == True, func.Integer)).label("conflicts")
    ).group_by(AuditLog.document_id).all()

    # 2. Get document titles for user readability
    doc_map = {doc.id: doc.title for doc in db.query(Document).all()}

    results = []
    for s in stats:
        total = s.total_queries or 1
        approval_rate = (s.approvals or 0) / total
        conflict_rate = (s.conflicts or 0) / total
        avg_confidence = s.avg_confidence or 0.0
        
        # 🛡️ Reliability Index Formula (Enterprise Grounded)
        # Approval Rate (40%) + Avg Confidence (40%) - Conflict Penalty (20%)
        # Normalizes performance into a 0.0 - 1.0 "Trust Score"
        reliability_index = (approval_rate * 0.4) + (avg_confidence * 0.4) - (conflict_rate * 0.2)
        
        # Clamp to 0-1 range
        reliability_index = max(0.0, min(1.0, reliability_index))

        results.append({
            "document_id": str(s.document_id),
            "title": doc_map.get(s.document_id, "Unknown Document"),
            "total_queries": total,
            "approval_rate": round(approval_rate, 3),
            "conflict_rate": round(conflict_rate, 3),
            "avg_confidence": round(avg_confidence, 3),
            "reliability_index": round(reliability_index, 3),
            "status": "stable" if reliability_index > 0.7 else "evaluating" if reliability_index > 0.4 else "unreliable"
        })

    # Sort by reliability index (highest first)
    return sorted(results, key=lambda x: x["reliability_index"], reverse=True)
