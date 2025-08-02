from app.repositories.library_repository import LibraryRepository
from app.services.embedding_service import EmbeddingService
from app.services.vector_index_service import VectorIndexService
from app.services.library_service import LibraryService
from app.services.document_service import DocumentService
from app.services.chunk_service import ChunkService

# Singleton instances shared across all routers
_library_repo = LibraryRepository()
_embedding_service = EmbeddingService()
_vector_index_service = VectorIndexService()

# Service layer instances that depend on repositories
_library_service = LibraryService(_library_repo)
_document_service = DocumentService(_library_repo)
_chunk_service = ChunkService(_library_repo)

def get_library_repository() -> LibraryRepository:
    """Get the shared LibraryRepository instance"""
    return _library_repo

def get_embedding_service() -> EmbeddingService:
    """Get the shared EmbeddingService instance"""
    return _embedding_service

def get_vector_index_service() -> VectorIndexService:
    """Get the shared VectorIndexService instance"""
    return _vector_index_service

def get_library_service() -> LibraryService:
    """Get the shared LibraryService instance"""
    return _library_service

def get_document_service() -> DocumentService:
    """Get the shared DocumentService instance"""
    return _document_service

def get_chunk_service() -> ChunkService:
    """Get the shared ChunkService instance"""
    return _chunk_service 