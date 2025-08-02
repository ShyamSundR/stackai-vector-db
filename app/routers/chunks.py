from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List
from uuid import UUID
from app.models import Chunk, CreateChunk, UpdateChunk
from app.services.chunk_service import ChunkService
from app.services.embedding_service import EmbeddingService
from app.core.dependencies import get_chunk_service, get_embedding_service

router = APIRouter()

@router.post("/", response_model=Chunk, status_code=status.HTTP_201_CREATED)
async def create_chunk(
    chunk_data: CreateChunk,
    document_id: UUID = Query(..., description="Document ID to add chunk to"),
    service: ChunkService = Depends(get_chunk_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
):
    """Create a new chunk in a document"""
    try:
        # Auto-generate embedding if not provided and service is available
        if not chunk_data.embedding and embedding_service.is_available():
            try:
                embedding = await embedding_service.generate_embedding(chunk_data.text)
                chunk_data.embedding = embedding
            except Exception as e:
                # Log the error but continue without embedding
                print(f"Warning: Could not generate embedding: {e}")
        
        chunk = await service.create_chunk(chunk_data, document_id)
        return chunk
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{chunk_id}", response_model=Chunk)
async def get_chunk(
    chunk_id: UUID,
    service: ChunkService = Depends(get_chunk_service)
):
    """Get a chunk by ID"""
    chunk = await service.get_chunk(chunk_id)
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chunk not found"
        )
    return chunk

@router.get("/document/{document_id}", response_model=List[Chunk])
async def get_chunks_by_document(
    document_id: UUID,
    service: ChunkService = Depends(get_chunk_service)
):
    """Get all chunks in a document"""
    try:
        return await service.get_chunks_by_document(document_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/library/{library_id}", response_model=List[Chunk])
async def get_chunks_by_library(
    library_id: UUID,
    service: ChunkService = Depends(get_chunk_service)
):
    """Get all chunks in a library"""
    try:
        return await service.get_chunks_by_library(library_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{chunk_id}", response_model=Chunk)
async def update_chunk(
    chunk_id: UUID,
    chunk_data: UpdateChunk,
    service: ChunkService = Depends(get_chunk_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
):
    """Update a chunk"""
    try:
        # Auto-generate embedding if text changed and no embedding provided
        if chunk_data.text and not chunk_data.embedding and embedding_service.is_available():
            try:
                embedding = await embedding_service.generate_embedding(chunk_data.text)
                chunk_data.embedding = embedding
            except Exception as e:
                # Log the error but continue without embedding
                print(f"Warning: Could not generate embedding: {e}")
        
        chunk = await service.update_chunk(chunk_id, chunk_data)
        if not chunk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chunk not found"
            )
        return chunk
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chunk(
    chunk_id: UUID,
    service: ChunkService = Depends(get_chunk_service)
):
    """Delete a chunk"""
    success = await service.delete_chunk(chunk_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chunk not found"
        )
    return None