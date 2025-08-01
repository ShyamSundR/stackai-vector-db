from fastapi import APIRouter, HTTPException, Depends, Query, status
from uuid import UUID
from typing import Optional
from app.models import Chunk, CreateChunk, UpdateChunk
from app.repositories.library_repository import LibraryRepository
from app.services.embedding_service import EmbeddingService
from app.core.dependencies import get_library_repository, get_embedding_service

router = APIRouter()

@router.post("/", response_model=Chunk, status_code=status.HTTP_201_CREATED)
async def create_chunk(
    chunk_data: CreateChunk,
    document_id: UUID = Query(..., description="Document ID to add chunk to"),
    repo: LibraryRepository = Depends(get_library_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
):
    """Create a new chunk in a document"""
    
    # Verify document exists
    document = repo.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Document not found"
        )
    
    try:
        # Handle auto-embedding
        embedding = chunk_data.embedding
        if chunk_data.auto_embed:
            if not chunk_data.text.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Text cannot be empty when auto_embed is enabled"
                )
            try:
                embedding = await embedding_service.generate_embedding(chunk_data.text)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to generate embedding: {str(e)}"
                )
        elif not embedding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either provide embedding vector or set auto_embed=true"
            )
        
        # Create chunk with processed embedding
        chunk = Chunk(
            text=chunk_data.text,
            embedding=embedding,
            metadata=chunk_data.metadata,
            document_id=document_id
        )
        
        result = repo.create_chunk(chunk, document_id)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to create chunk"
        )

@router.get("/{chunk_id}", response_model=Chunk)
async def get_chunk(
    chunk_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Get a chunk by ID"""
    chunk = repo.get_chunk(chunk_id)
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Chunk not found"
        )
    return chunk

@router.get("/document/{document_id}", response_model=list[Chunk])
async def get_chunks_by_document(
    document_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Get all chunks for a document"""
    document = repo.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Document not found"
        )
    return repo.get_document_chunks(document_id)

@router.get("/library/{library_id}", response_model=list[Chunk])
async def get_chunks_by_library(
    library_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Get all chunks for a library"""
    library = repo.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Library not found"
        )
    return repo.get_library_chunks(library_id)

@router.put("/{chunk_id}", response_model=Chunk)
async def update_chunk(
    chunk_id: UUID,
    chunk_data: UpdateChunk,
    repo: LibraryRepository = Depends(get_library_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
):
    """Update a chunk"""
    chunk = repo.get_chunk(chunk_id)
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Chunk not found"
        )
    
    try:
        # Handle auto-embedding for updates
        update_data = chunk_data.dict(exclude_unset=True)
        if chunk_data.auto_embed and chunk_data.text:
            if not chunk_data.text.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Text cannot be empty when auto_embed is enabled"
                )
            try:
                update_data['embedding'] = await embedding_service.generate_embedding(chunk_data.text)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to generate embedding: {str(e)}"
                )
        
        # Remove auto_embed from update data as it's not stored in the model
        update_data.pop('auto_embed', None)
        
        updated_chunk = repo.update_chunk(chunk_id, **update_data)
        return updated_chunk
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update chunk: {str(e)}"
        )

@router.delete("/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chunk(
    chunk_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Delete a chunk"""
    chunk = repo.get_chunk(chunk_id)
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Chunk not found"
        )
    repo.delete_chunk(chunk_id)
    return None