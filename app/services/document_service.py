from typing import Optional, List
from uuid import UUID
from app.models import Document, DocumentCreate, DocumentUpdate
from app.repositories.library_repository import LibraryRepository


class DocumentService:
    """Service layer for document operations with business logic"""
    
    def __init__(self, repository: LibraryRepository):
        self._repository = repository
    
    async def create_document(self, document_data: DocumentCreate) -> Document:
        """Create a new document with business validation"""
        # Business logic validation
        if len(document_data.title.strip()) < 1:
            raise ValueError("Document title cannot be empty")
        
        if document_data.title.strip() != document_data.title:
            raise ValueError("Document title cannot have leading or trailing whitespace")
        
        # Check if library exists
        library = self._repository.get_library(document_data.library_id)
        if not library:
            raise ValueError(f"Library with ID {document_data.library_id} does not exist")
        
        # Check for duplicate titles within the same library
        existing_docs = self._repository.get_library_documents(document_data.library_id)
        for doc in existing_docs:
            if doc.title.lower() == document_data.title.lower():
                raise ValueError(f"Document with title '{document_data.title}' already exists in this library")
        
        # Delegate to repository
        return self._repository.create_document(document_data)
    
    async def get_document(self, document_id: UUID) -> Optional[Document]:
        """Get a document by ID"""
        return self._repository.get_document(document_id)
    
    async def get_documents_by_library(self, library_id: UUID) -> List[Document]:
        """Get all documents in a library"""
        # Verify library exists
        library = self._repository.get_library(library_id)
        if not library:
            raise ValueError(f"Library with ID {library_id} does not exist")
        
        return self._repository.get_library_documents(library_id)
    
    async def update_document(self, document_id: UUID, document_data: DocumentUpdate) -> Optional[Document]:
        """Update a document with business validation"""
        # Check if document exists
        existing_document = self._repository.get_document(document_id)
        if not existing_document:
            return None
        
        # Business logic validation
        if document_data.title and len(document_data.title.strip()) < 1:
            raise ValueError("Document title cannot be empty")
        
        if document_data.title and document_data.title.strip() != document_data.title:
            raise ValueError("Document title cannot have leading or trailing whitespace")
        
        # Check for duplicate titles within the same library (excluding current document)
        if document_data.title:
            existing_docs = self._repository.get_library_documents(existing_document.library_id)
            for doc in existing_docs:
                if doc.id != document_id and doc.title.lower() == document_data.title.lower():
                    raise ValueError(f"Document with title '{document_data.title}' already exists in this library")
        
        # Delegate to repository
        return self._repository.update_document(document_id, document_data)
    
    async def delete_document(self, document_id: UUID) -> bool:
        """Delete a document with business logic checks"""
        # Check if document exists
        existing_document = self._repository.get_document(document_id)
        if not existing_document:
            return False
        
        # Business logic: Could add checks here like:
        # - Prevent deletion if document has important chunks
        # - Log deletion for audit purposes
        # - Send notifications
        
        # Delegate to repository
        return self._repository.delete_document(document_id)