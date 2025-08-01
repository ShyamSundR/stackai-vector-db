from typing import Optional
from uuid import UUID
from app.models import Document, DocumentCreate, DocumentUpdate
from datetime import datetime


class DocumentService:
    """Service layer for document operations"""
    
    def __init__(self):
        # In-memory storage for now - will be replaced with proper persistence
        self._documents: dict[UUID, Document] = {}
    
    async def create_document(self, document_data: DocumentCreate) -> Document:
        """Create a new document"""
        doc = Document(**document_data.dict())
        self._documents[doc.id] = doc
        return doc
    
    async def get_document(self, document_id: UUID) -> Optional[Document]:
        """Get a document by ID"""
        return self._documents.get(document_id)
    
    async def get_documents_by_library(self, library_id: UUID) -> list[Document]:
        """Get all documents in a library"""
        return [doc for doc in self._documents.values() if doc.library_id == library_id]
    
    async def update_document(self, document_id: UUID, document_data: DocumentUpdate) -> Optional[Document]:
        """Update a document"""
        doc = self._documents.get(document_id)
        if not doc:
            return None
        update_data = document_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(doc, key, value)
        doc.updated_at = datetime.utcnow()
        self._documents[document_id] = doc
        return doc
    
    async def delete_document(self, document_id: UUID) -> bool:
        """Delete a document"""
        return self._documents.pop(document_id, None) is not None