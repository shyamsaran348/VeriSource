from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_student, get_db
from app.documents.service import (
    get_document_by_id,
    validate_document_access,
)
from app.query.schemas import QueryRequest, QueryResponse, EvidenceBlock
from app.rag.retriever import retrieve
from app.rag.evidence import extract_evidence
from app.rag.conflict import detect_conflict

# 🔹 Phase 5 imports
from app.llm.provider import generate_answer
from app.llm.response_parser import parse_llm_response

# 🔒 Phase 6 imports
from app.decision.engine import make_decision

# 🟦 Phase 7 import
from app.audit.logger import log_query_interaction


router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/", response_model=QueryResponse)
def query_document(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_student),  # 🔒 Student only — admin blocked (403)
):
    """
    Phase 7 — Governance + Audit-Enforced Answering

    Access control:   Student only (admin → 403)
    Governance:       Mode match + active policy version enforced
    Isolation:        Single document scope — never touches other collections
    Evidence:         Raw text chunks + similarity score + chunk_id
    Generation:       LLM sees ONLY evidence text + query
    Control:          System decides approval/refusal (LLM cannot override)
    Audit:            Every interaction logged (approved + refused)
    """

    # 1️⃣ Validate document exists
    document = get_document_by_id(db, str(request.document_id))

    # 2️⃣ Enforce governance rules
    validate_document_access(document, request.mode)

    # 3️⃣ Strict single-document retrieval
    raw_results = retrieve(str(request.document_id), request.query, request.mode)

    # 4️⃣ Structured evidence extraction
    evidence_dicts = extract_evidence(raw_results, request.query)
    evidence_blocks = [EvidenceBlock(**block) for block in evidence_dicts]

    # 5️⃣ Mode-aware conflict detection
    conflict = detect_conflict(evidence_dicts, request.mode)

    # ---------------------------------------------------
    # 🔒 Controlled LLM Generation
    # ---------------------------------------------------

    # Extract ONLY raw text for LLM
    evidence_texts = [block["text"] for block in evidence_dicts]

    raw_answer = generate_answer(
        mode=request.mode,
        query=request.query,
        evidence_blocks=evidence_texts,
    )

    parsed = parse_llm_response(raw_answer)

    # ---------------------------------------------------
    # 🔒 PHASE 6 — SYSTEM-LEVEL GOVERNANCE DECISION
    # ---------------------------------------------------

    similarities = [block.similarity for block in evidence_blocks]

    decision_obj = make_decision(
        mode=request.mode,
        query_str=request.query,
        similarities=similarities,
        conflict_flag=conflict,
        model_flag_insufficient=parsed["model_flag_insufficient"],
    )

    # ---------------------------------------------------
    # 🟦 PHASE 7 — AUDIT LOGGING (ALWAYS EXECUTES)
    # ---------------------------------------------------

    final_answer = None
    if decision_obj["decision"] == "approved":
        if parsed["answer"] is not None:
            # LLM generated a real answer
            final_answer = parsed["answer"]
        else:
            # Governance approved but LLM flagged INSUFFICIENT_EVIDENCE (known ~80% FP rate).
            # Fall back to the top retrieved evidence text so the approved decision
            # still delivers useful information to the student.
            fallback_texts = evidence_texts[:2] if evidence_texts else []
            if fallback_texts:
                final_answer = " [...] ".join(fallback_texts)

    log_query_interaction(
        db=db,
        user_id=current_user.id,
        document_id=request.document_id,
        mode=request.mode,
        query=request.query,
        decision=decision_obj["decision"],
        confidence_score=decision_obj["confidence_score"],
        conflict_detected=conflict,
    )

    # ---------------------------------------------------
    # 🔒 Final Governed Response
    # ---------------------------------------------------

    from datetime import datetime
    from app.audit.logger import hash_query

    return QueryResponse(
        document_id=request.document_id,
        mode=request.mode,
        evidence=evidence_blocks,
        conflict_detected=conflict,
        answer=final_answer,  # None if refused
        model_flag_insufficient=parsed["model_flag_insufficient"],
        decision=decision_obj["decision"],
        confidence_score=decision_obj["confidence_score"],
        reason=decision_obj["reason"],
        explanation=decision_obj["explanation"],
        query_hash=hash_query(request.query),
        timestamp=datetime.utcnow().isoformat()
    )