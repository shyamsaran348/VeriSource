from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.documents.models import Document


def deactivate_previous_policy_versions(db: Session, name: str):
    db.query(Document).filter(
        Document.name == name,
        Document.mode == "policy",
        Document.is_active == True
    ).update({"is_active": False})


def create_document(
    db: Session,
    name: str,
    mode: str,
    version: str,
    authority: str,
    file_hash: str
):
    try:
        if mode == "policy":
            deactivate_previous_policy_versions(db, name)

        document = Document(
            name=name,
            mode=mode,
            version=version,
            authority=authority,
            hash=file_hash,
            is_active=True
        )

        db.add(document)
        db.flush()
        return document

    except SQLAlchemyError:
        db.rollback()
        raise


# =====================================
# PHASE 4 — Retrieval Support
# =====================================

def get_document_by_id(db: Session, document_id: str) -> Document:
    document = db.query(Document).filter(
        Document.document_id == document_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    return document


def validate_document_access(document: Document, mode: str):
    """
    Enforces:
    - Mode match
    - Active version rule (for policy)
    """

    if document.mode != mode:
        raise HTTPException(
            status_code=400,
            detail="Mode mismatch for selected document."
        )

    if mode == "policy" and not document.is_active:
        raise HTTPException(
            status_code=400,
            detail="Only latest active policy version can be queried."
        )