from typing import Optional, List
from uuid import UUID
from app.models import Chunk, CreateChunk, UpdateChunk
from app.repositories.library_repository import LibraryRepository


class ChunkService:
    """Service layer for chunk operations with business logic"""
    
    def __init__(self, repository: LibraryRepository):
        self._repository = repository
    
    async def create_chunk(self, chunk_data: CreateChunk, document_id: UUID) -> Chunk:
        """Create a new chunk with business validation"""
        # Business logic validation
        if len(chunk_data.text.strip()) < 1:
            raise ValueError("Chunk text cannot be empty")
        
        if len(chunk_data.text) > 10000:  # 10KB limit
            raise ValueError("Chunk text cannot exceed 10,000 characters")
        
        # Check if document exists
        document = self._repository.get_document(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} does not exist")
        
        # Business logic: Validate embedding if provided
        if chunk_data.embedding:
            if len(chunk_data.embedding) == 0:
                raise ValueError("Embedding cannot be empty if provided")
            if not all(isinstance(x, (int, float)) for x in chunk_data.embedding):
                raise ValueError("Embedding must contain only numeric values")
        
        # Create a proper Chunk object from CreateChunk data
        from app.models import Chunk
        chunk = Chunk(
            text=chunk_data.text,
            embedding=chunk_data.embedding or [],
            metadata=chunk_data.metadata,
            document_id=document_id
        )
        
        # Delegate to repository
        return self._repository.create_chunk(chunk, document_id)
    
    async def get_chunk(self, chunk_id: UUID) -> Optional[Chunk]:
        """Get a chunk by ID"""
        return self._repository.get_chunk(chunk_id)
    
    async def get_chunks_by_document(self, document_id: UUID) -> List[Chunk]:
        """Get all chunks in a document"""
        # Verify document exists
        document = self._repository.get_document(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} does not exist")
        
        return self._repository.get_document_chunks(document_id)
    
    async def get_chunks_by_library(self, library_id: UUID) -> List[Chunk]:
        """Get all chunks in a library"""
        # Verify library exists
        library = self._repository.get_library(library_id)
        if not library:
            raise ValueError(f"Library with ID {library_id} does not exist")
        
        return self._repository.get_library_chunks(library_id)
    
    async def update_chunk(self, chunk_id: UUID, chunk_data: UpdateChunk) -> Optional[Chunk]:
        """Update a chunk with business validation"""
        # Check if chunk exists
        existing_chunk = self._repository.get_chunk(chunk_id)
        if not existing_chunk:
            return None
        
        # Business logic validation
        if chunk_data.text and len(chunk_data.text.strip()) < 1:
            raise ValueError("Chunk text cannot be empty")
        
        if chunk_data.text and len(chunk_data.text) > 10000:
            raise ValueError("Chunk text cannot exceed 10,000 characters")
        
        # Validate embedding if provided
        if chunk_data.embedding is not None:
            if len(chunk_data.embedding) == 0:
                raise ValueError("Embedding cannot be empty if provided")
            if not all(isinstance(x, (int, float)) for x in chunk_data.embedding):
                raise ValueError("Embedding must contain only numeric values")
        
        # Delegate to repository
        return self._repository.update_chunk(chunk_id, chunk_data)
    
    async def delete_chunk(self, chunk_id: UUID) -> bool:
        """Delete a chunk with business logic checks"""
        # Check if chunk exists
        existing_chunk = self._repository.get_chunk(chunk_id)
        if not existing_chunk:
            return False
        
        # Business logic: Could add checks here like:
        # - Log deletion for audit purposes
        # - Update search indexes
        # - Send notifications
        
        # Delegate to repository
        return self._repository.delete_chunk(chunk_id)
