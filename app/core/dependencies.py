from app.repositories.library_repository import LibraryRepository
from app.services.embedding_service import EmbeddingService
from app.services.vector_index_service import VectorIndexService

# Singleton instances shared across all routers
_library_repo = LibraryRepository()
_embedding_service = EmbeddingService()
_vector_index_service = VectorIndexService()

def get_library_repository() -> LibraryRepository:
    """Get the shared LibraryRepository instance"""
    return _library_repo

def get_embedding_service() -> EmbeddingService:
    """Get the shared EmbeddingService instance"""
    return _embedding_service

def get_vector_index_service() -> VectorIndexService:
    """Get the shared VectorIndexService instance"""
    return _vector_index_service 