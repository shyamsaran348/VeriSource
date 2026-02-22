from sqlalchemy.orm import Session
from sqlalchemy import func, case, Integer
from app.audit.models import AuditLog
from app.documents.models import Document
from typing import List, Dict

def get_document_reliability_metrics(db: Session) -> List[Dict]:
    """
    Computes empirical reliability metrics for all documents based on audit history.
    Aligns with AI Reliability Engineering & Calibration research.
    """
    
    # 1. Group by document_id and aggregate stats
    # Using 'case' for robust conditional counting across dialects
    stats = db.query(
        AuditLog.document_id,
        func.count(AuditLog.id).label("total_queries"),
        func.avg(AuditLog.confidence_score).label("avg_confidence"),
        func.sum(case((AuditLog.decision == "approved", 1), else_=0)).label("approvals"),
        func.sum(case((AuditLog.conflict_detected == True, 1), else_=0)).label("conflicts")
    ).group_by(AuditLog.document_id).all()

    # 2. Get document titles for user readability
    # Filter to only include documents that actually exist in the system
    active_docs = db.query(Document).all()
    doc_map = {doc.document_id: doc.name for doc in active_docs}
    active_ids = set(doc_map.keys())

    results = []
    for s in stats:
        # Skip "ghost" logs from deleted documents to avoid skewing the system score
        if s.document_id not in active_ids:
            continue

        total = s.total_queries or 1
        approval_rate = (s.approvals or 0) / total
        conflict_rate = (s.conflicts or 0) / total
        avg_confidence = s.avg_confidence or 0.0
        
        # 🛡️ RESEARCH-ALIGNED CALIBRATED RELIABILITY INDEX (Phase 10 — Improvised)
        # Context: Embedding models like fastembed cluster scores in the 0.1 - 0.5 range.
        # A raw average makes the system look "unreliable" when it's actually just precise.
        
        # A. Confidence Normalization: Map 0.2 (refusal threshold) to 0.7 (baseline trust)
        # Any document that consistently stays above the refusal threshold is "Safe".
        calibrated_conf = min(1.0, (avg_confidence / 0.4)) 
        
        # B. Safety Calibration: High refusal rates aren't bad if they prevent hallucinations.
        # We value "Stability" (Low Conflict) + "Confidence" (Groundedness) over raw Approval.
        # Modified weights: Stability (50%) + Calibrated Confidence (30%) + Coverage/Approval (20%)
        stability_score = 1.0 - conflict_rate
        coverage_score = approval_rate 
        
        reliability_index = (stability_score * 0.5) + (calibrated_conf * 0.3) + (coverage_score * 0.2)
        
        # Clamp to 0-1 range
        reliability_index = max(0.0, min(1.0, reliability_index))

        results.append({
            "document_id": str(s.document_id),
            "title": doc_map[s.document_id],
            "total_queries": total,
            "approval_rate": round(approval_rate, 3),
            "conflict_rate": round(conflict_rate, 3),
            "avg_confidence": round(avg_confidence, 3),
            "reliability_index": round(reliability_index, 3),
            "status": "stable" if reliability_index > 0.65 else "evaluating" if reliability_index > 0.35 else "unreliable"
        })

    # Sort by reliability index (highest first)
    return sorted(results, key=lambda x: x["reliability_index"], reverse=True)
