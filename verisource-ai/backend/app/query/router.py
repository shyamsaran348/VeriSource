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

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/", response_model=QueryResponse)
def query_document(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_student),  # 🔒 Student only — admin blocked (403)
):
    """
    Phase 6 — Governance-Enforced Answering

    Access control:   Student only (admin → 403)
    Governance:       Mode match + active policy version enforced
    Isolation:        Single document scope — never touches other collections
    Evidence:         Raw text chunks + similarity score + chunk_id
    Generation:       LLM sees ONLY evidence text + query
    Control:          System decides approval/refusal (LLM cannot override)
    """

    # 1️⃣ Validate document exists
    document = get_document_by_id(db, str(request.document_id))

    # 2️⃣ Enforce governance rules
    validate_document_access(document, request.mode)

    # 3️⃣ Strict single-document retrieval
    raw_results = retrieve(str(request.document_id), request.query)

    # 4️⃣ Structured evidence extraction
    evidence_dicts = extract_evidence(raw_results)

    evidence_blocks = [EvidenceBlock(**block) for block in evidence_dicts]

    # 5️⃣ Mode-aware conflict detection
    conflict = detect_conflict(evidence_dicts, request.mode)

    # ---------------------------------------------------
    # 🔒 Controlled LLM Generation
    # ---------------------------------------------------

    # Extract ONLY raw text for LLM
    evidence_texts = [block["text"] for block in evidence_dicts]

    # LLM generation (LLM sees only query + evidence text)
    raw_answer = generate_answer(
        mode=request.mode,
        query=request.query,
        evidence_blocks=evidence_texts,
    )

    # Parse model output (detect INSUFFICIENT_EVIDENCE flag)
    parsed = parse_llm_response(raw_answer)

    # ---------------------------------------------------
    # 🔒 PHASE 6 — SYSTEM-LEVEL GOVERNANCE DECISION
    # ---------------------------------------------------

    similarities = [block.similarity for block in evidence_blocks]

    decision_obj = make_decision(
        mode=request.mode,
        similarities=similarities,
        conflict_flag=conflict,
        model_flag_insufficient=parsed["model_flag_insufficient"],
    )

    # 🚫 If refused → block answer completely
    if decision_obj["decision"] == "refused":
        return QueryResponse(
            document_id=request.document_id,
            mode=request.mode,
            evidence=evidence_blocks,
            conflict_detected=conflict,
            answer=None,  # BLOCKED
            model_flag_insufficient=parsed["model_flag_insufficient"],
            decision="refused",
            confidence_score=decision_obj["confidence_score"],
            reason=decision_obj["reason"],
        )

    # ✅ If approved → allow answer
    return QueryResponse(
        document_id=request.document_id,
        mode=request.mode,
        evidence=evidence_blocks,
        conflict_detected=conflict,
        answer=parsed["answer"],
        model_flag_insufficient=parsed["model_flag_insufficient"],
        decision="approved",
        confidence_score=decision_obj["confidence_score"],
        reason=decision_obj["reason"],
    )