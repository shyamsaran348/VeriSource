from pydantic import BaseModel, UUID4, field_validator
from typing import Literal, List, Optional


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
    score: float


class QueryResponse(BaseModel):
    document_id: UUID4
    mode: str
    evidence: List[EvidenceBlock]
    conflict_detected: bool
    answer: Optional[str] = None
    model_flag_insufficient: bool = False