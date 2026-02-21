from pydantic import BaseModel
from uuid import UUID


class DocumentCreate(BaseModel):
    name: str
    mode: str  # policy / research
    version: str
    authority: str


class DocumentResponse(BaseModel):
    document_id: UUID
    name: str
    mode: str
    version: str
    authority: str
    is_active: bool

    class Config:
        from_attributes = True