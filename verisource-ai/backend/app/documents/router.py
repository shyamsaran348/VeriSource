from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.documents.models import Document
from app.core.dependencies import require_admin
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/documents", tags=["Documents"])

class DocumentResponse(BaseModel):
    document_id: str
    document_name: str
    mode: str
    version: str
    authority: Optional[str]
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[DocumentResponse])
def get_documents(mode: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Document)
    if mode:
        query = query.filter(Document.mode == mode)
        if mode == "policy":
            query = query.filter(Document.is_active == True)
            
    documents = query.order_by(Document.created_at.desc()).all()
    
    # Map 'name' to 'document_name' for frontend compatibility
    return [
        {
            "document_id": str(doc.document_id),
            "document_name": doc.name,
            "mode": doc.mode,
            "version": doc.version,
            "authority": doc.authority,
            "active": doc.is_active,
            "created_at": doc.created_at
        }
        for doc in documents
    ]

@router.delete("/{document_id}/")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    from app.documents.service import get_document_by_id
    from app.rag.vector_store import get_client
    
    document = get_document_by_id(db, document_id)
    if not document:
        return {"message": "Document not found"}

    try:
        get_client().delete_collection(name=f"doc_{document_id}")
    except Exception as e:
        print(f"Vector collection not found or could not be deleted: {e}")

    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}
