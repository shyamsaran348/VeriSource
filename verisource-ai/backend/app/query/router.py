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

from app.llm.provider import generate_answer
from app.llm.response_parser import parse_llm_response
from app.decision.engine import make_decision
from app.audit.logger import log_query_interaction


router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/", response_model=QueryResponse)
def query_document(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_student), 
):
    """
    Governed Semantic Search: The primary entry point for policy verification.
    
    This endpoint implements a strict 'local-RAG' pattern:
    1. Authorization & Access Control (Student only)
    2. Single-Document Vector Retrieval
    3. Stage 1 Governance: Signal-to-noise gating (Pre-LLM)
    4. Stage 2 Governance: Sentinel-based uncertainty detection (Post-LLM)
    5. Privacy-Preserving Audit Logging
    """

    # 1. Access Control: Ensure the user is authorized for the document and mode
    document = get_document_by_id(db, str(request.document_id))
    validate_document_access(document, request.mode)

    # 2. Retrieval: High-precision semantic chunk extraction
    raw_results = retrieve(str(request.document_id), request.query, request.mode)

    # 3. Evidence Processing: Scoring, acronym boosting, and block structuring
    evidence_dicts = extract_evidence(raw_results, request.query)
    evidence_blocks = [EvidenceBlock(**block) for block in evidence_dicts]
    conflict = detect_conflict(evidence_dicts, request.mode)

    # 4. Stage 1 Governance Decision (Before expensive LLM call)
    similarities = [block.similarity for block in evidence_blocks]
    decision_obj = make_decision(
        mode=request.mode,
        query_str=request.query,
        similarities=similarities,
        conflict_flag=conflict,
        model_flag_insufficient=False,
    )

    final_answer = None
    model_flag_insufficient = False

    # 5. LLM Synthesis (Only if Stage 1 is 'Approved')
    if decision_obj["decision"] == "approved":
        evidence_texts = [block.text for block in evidence_blocks]

        # Call Groq/Llama-3 with strict 'Evidence-Only' instructions
        raw_answer = generate_answer(
            mode=request.mode,
            query=request.query,
            evidence_blocks=evidence_texts,
        )

        # Parse LLM response for hidden sentinel tokens
        parsed = parse_llm_response(raw_answer)
        model_flag_insufficient = parsed["model_flag_insufficient"]
        
        # Stage 2 Governance: Re-evaluate decision if LLM flagged insufficiency
        if model_flag_insufficient:
            decision_obj = make_decision(
                mode=request.mode,
                query_str=request.query,
                similarities=similarities,
                conflict_flag=conflict,
                model_flag_insufficient=True,
            )
        
        # Construct final answer if still approved
        if decision_obj["decision"] == "approved":
            final_answer = parsed["answer"] or " [...] ".join(evidence_texts[:2])

    # 6. Audit Logging: Record interaction without storing raw query text (GDPR)
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

    # 7. Final Governed Response Construction
    from datetime import datetime
    from app.audit.logger import hash_query

    return QueryResponse(
        document_id=request.document_id,
        mode=request.mode,
        evidence=evidence_blocks,
        conflict_detected=conflict,
        answer=final_answer,
        model_flag_insufficient=model_flag_insufficient,
        decision=decision_obj["decision"],
        confidence_score=decision_obj["confidence_score"],
        reason=decision_obj["reason"],
        explanation=decision_obj.get("explanation"),
        query_hash=hash_query(request.query),
        timestamp=datetime.utcnow().isoformat()
    )