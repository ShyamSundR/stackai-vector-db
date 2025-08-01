from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from uuid import UUID
from datetime import datetime

from app.models import Chunk, CreateChunk, UpdateChunk
from app.core.dependencies import get_library_repository
from app.repositories.library_repository import LibraryRepository
from app.services.embedding_service import embedding_service

router = APIRouter()


@router.post("/", response_model=Chunk, status_code=201)
async def create_chunk(
    chunk_data: CreateChunk,
    document_id: UUID = Query(..., description="ID of the document to add the chunk to"),
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Create a new chunk in a document"""
    # Check if document exists
    document = repo.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Handle embedding generation
    embedding = chunk_data.embedding
    
    if embedding is None and chunk_data.auto_embed:
        # Generate embedding using Cohere API
        if not embedding_service.is_available():
            raise HTTPException(
                status_code=400, 
                detail="Embedding service not available. Please provide manual embedding or configure Cohere API key."
            )
        
        try:
            embedding = await embedding_service.generate_embedding(chunk_data.text)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate embedding: {str(e)}"
            )
    elif embedding is None:
        raise HTTPException(
            status_code=400,
            detail="Either provide embedding vector or set auto_embed=true"
        )
    
    # Create chunk object
    chunk = Chunk(
        document_id=document_id,
        text=chunk_data.text,
        embedding=embedding,
        metadata=chunk_data.metadata,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Save chunk via repository
    created_chunk = repo.create_chunk(chunk, document_id)
    if not created_chunk:
        raise HTTPException(status_code=500, detail="Failed to create chunk")
    
    return created_chunk


@router.get("/{chunk_id}", response_model=Chunk)
async def get_chunk(
    chunk_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Get a chunk by ID"""
    chunk = repo.get_chunk(chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return chunk


@router.get("/document/{document_id}", response_model=List[Chunk])
async def get_chunks_by_document(
    document_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Get all chunks in a document"""
    document = repo.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    chunks = repo.get_document_chunks(document_id)
    return chunks


@router.get("/library/{library_id}", response_model=List[Chunk])
async def get_chunks_by_library(
    library_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Get all chunks in a library"""
    library = repo.get_library(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    chunks = repo.get_library_chunks(library_id)
    return chunks


@router.put("/{chunk_id}", response_model=Chunk)
async def update_chunk(
    chunk_id: UUID,
    chunk_data: UpdateChunk,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Update a chunk"""
    existing_chunk = repo.get_chunk(chunk_id)
    if not existing_chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    # Handle embedding regeneration if text is updated
    embedding = chunk_data.embedding
    text = chunk_data.text or existing_chunk.text
    
    if chunk_data.text and chunk_data.auto_embed:
        # Regenerate embedding using Cohere API
        if not embedding_service.is_available():
            raise HTTPException(
                status_code=400,
                detail="Embedding service not available. Please provide manual embedding or configure Cohere API key."
            )
        
        try:
            embedding = await embedding_service.generate_embedding(text)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate embedding: {str(e)}"
            )
    elif embedding is None:
        # Keep existing embedding if no new one provided
        embedding = existing_chunk.embedding
    
    # Prepare update data
    update_data = {}
    if chunk_data.text is not None:
        update_data['text'] = text
    if embedding is not None:
        update_data['embedding'] = embedding
    if chunk_data.metadata is not None:
        update_data['metadata'] = chunk_data.metadata
    
    update_data['updated_at'] = datetime.utcnow()
    
    # Update chunk
    updated_chunk = repo.update_chunk(chunk_id, **update_data)
    if not updated_chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    return updated_chunk


@router.delete("/{chunk_id}")
async def delete_chunk(
    chunk_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Delete a chunk"""
    success = repo.delete_chunk(chunk_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return {"message": "Chunk deleted successfully"}