from pydantic import BaseModel, UUID4, field_validator
from typing import Literal, List, Optional, Dict


class QueryRequest(BaseModel):
    mode: Literal["policy", "research"]
    document_id: UUID4
    query: str

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query cannot be empty.")
        return v.strip()


class EvidenceBlock(BaseModel):
    chunk_id: str
    text: str
    similarity: float  # 🔹 renamed from score → similarity (Phase 6 requirement)


class QueryResponse(BaseModel):
    document_id: UUID4
    mode: str

    evidence: List[EvidenceBlock]
    conflict_detected: bool

    # Phase 5 fields
    answer: Optional[str] = None
    model_flag_insufficient: bool = False

    # 🔒 Phase 6 fields
    decision: Literal["approved", "refused"]
    confidence_score: float
    reason: str
    
    # 🧭 Phase 9 — Counterfactual Refusal Explanation
    explanation: Optional[Dict] = None
    
    # Traceability
    query_hash: Optional[str] = None
    timestamp: Optional[str] = None