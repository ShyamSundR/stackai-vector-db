from typing import Optional
from uuid import UUID
from app.models import Chunk, CreateChunk, UpdateChunk


class ChunkService:
    """Service layer for chunk operations"""
    
    def __init__(self):
        # In-memory storage for now - will be replaced with proper persistence
        self._chunks: dict[UUID, Chunk] = {}
    
    async def create_chunk(self, chunk_data: CreateChunk) -> Chunk:
        chunk = Chunk(**chunk_data.dict())
        self._chunks[chunk.id] = chunk
        return chunk
    
    async def get_chunk(self, chunk_id: UUID) -> Optional[Chunk]:
        return self._chunks.get(chunk_id)
    
    async def get_chunks_by_document(self, document_id: UUID) -> list[Chunk]:
        return [chunk for chunk in self._chunks.values() if getattr(chunk, 'document_id', None) == document_id]
    
    async def get_chunks_by_library(self, library_id: UUID) -> list[Chunk]:
        return [chunk for chunk in self._chunks.values() if getattr(chunk, 'library_id', None) == library_id]
    
    async def update_chunk(self, chunk_id: UUID, chunk_data: UpdateChunk) -> Optional[Chunk]:
        chunk = self._chunks.get(chunk_id)
        if not chunk:
            return None
        update_data = chunk_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(chunk, key, value)
        self._chunks[chunk_id] = chunk
        return chunk
    
    async def delete_chunk(self, chunk_id: UUID) -> bool:
        return self._chunks.pop(chunk_id, None) is not None
