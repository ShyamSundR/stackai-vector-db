from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List, Dict, Any
from app.models import Chunk
from app.repositories.library_repository import LibraryRepository
from app.services.vector_index_service import VectorIndexService, VectorSearchResult
from app.services.embedding_service import EmbeddingService
from app.core.dependencies import get_library_repository, get_vector_index_service, get_embedding_service

router = APIRouter()

class SearchRequest(BaseModel):
    """Request model for vector similarity search"""
    query_embedding: Optional[List[float]] = Field(
        default=None, 
        description="Vector embedding for similarity search"
    )
    query_text: Optional[str] = Field(
        default=None,
        description="Text to auto-embed for similarity search"
    )
    k: int = Field(default=10, description="Number of similar chunks to return")
    similarity_metric: str = Field(default="cosine", description="Similarity metric (cosine, euclidean, dot_product)")
    metadata_filter: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Advanced metadata filtering conditions"
    )

class SearchResultItem(BaseModel):
    """Response model for search results"""
    chunk: Chunk
    distance: float
    similarity: float

class IndexRequest(BaseModel):
    """Request model for index operations"""
    index_type: str = Field(description="Type of index (brute_force, kdtree)")

class IndexTypeRequest(BaseModel):
    """Request model for setting index type"""
    index_type: str = Field(description="Type of index to set")

@router.post("/libraries/{library_id}/index", status_code=status.HTTP_200_OK)
async def build_index(
    library_id: UUID,
    index_type: str = Query(..., description="Type of index to build"),
    repo: LibraryRepository = Depends(get_library_repository),
    vector_service: VectorIndexService = Depends(get_vector_index_service)
):
    """Build a vector index for a library"""
    # Verify library exists
    library = repo.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Library not found"
        )
    
    # Get chunks for the library
    chunks = repo.get_library_chunks(library_id)
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No chunks found for this library"
        )
    
    try:
        # Set index type and index the library
        vector_service.set_index_type(library_id, index_type)
        await vector_service.index_library(library_id, chunks)
        
        return {
            "message": f"Successfully built {index_type} index for library {library_id}",
            "library_id": str(library_id),
            "index_type": index_type,
            "chunk_count": len(chunks)
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to index library: {str(e)}"
        )

@router.post("/libraries/{library_id}/search", response_model=List[SearchResultItem])
async def search_similar_chunks(
    library_id: UUID,
    request: SearchRequest,
    repo: LibraryRepository = Depends(get_library_repository),
    vector_service: VectorIndexService = Depends(get_vector_index_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
):
    """Search for similar chunks in a library using vector similarity"""
    # Verify library exists
    library = repo.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Library not found"
        )
    
    try:
        # Handle query embedding
        query_embedding = request.query_embedding
        
        # If text provided, generate embedding
        if request.query_text and not query_embedding:
            if not embedding_service.is_available():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Embedding service not available. Please provide query_embedding or configure Cohere API key."
                )
            try:
                query_embedding = await embedding_service.generate_embedding(request.query_text)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to generate embedding: {str(e)}"
                )
        
        if not query_embedding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either query_embedding or query_text must be provided"
            )
        
        # Perform search
        search_results = await vector_service.search_similar_chunks(
            library_id=library_id,
            query_embedding=query_embedding,
            k=request.k,
            similarity_metric=request.similarity_metric,
            metadata_filter=request.metadata_filter
        )
        
        # Format results for response
        formatted_results = []
        for result in search_results:
            formatted_results.append(SearchResultItem(
                chunk=result.chunk,
                distance=result.distance,
                similarity=result.similarity
            ))
        
        return formatted_results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Search failed: {str(e)}"
        )

@router.post("/libraries/{library_id}/index_type", status_code=status.HTTP_200_OK)
async def set_index_type(
    library_id: UUID,
    index_type: str = Query(..., description="Type of index to set"),
    repo: LibraryRepository = Depends(get_library_repository),
    vector_service: VectorIndexService = Depends(get_vector_index_service)
):
    """Set the index type for a library"""
    # Verify library exists
    library = repo.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Library not found"
        )
    
    try:
        vector_service.set_index_type(library_id, index_type)
        return {
            "message": f"Index type set to {index_type} for library {library_id}",
            "library_id": str(library_id),
            "index_type": index_type
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set index type: {str(e)}"
        )

@router.get("/libraries/{library_id}/index", status_code=status.HTTP_200_OK)
async def get_index_info(
    library_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository),
    vector_service: VectorIndexService = Depends(get_vector_index_service)
):
    """Get index information for a library"""
    # Verify library exists
    library = repo.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Library not found"
        )
    
    index_type = vector_service.get_index_type(library_id)
    chunks = repo.get_library_chunks(library_id)
    
    return {
        "library_id": str(library_id),
        "index_type": index_type,
        "chunk_count": len(chunks),
        "indexed": index_type is not None
    }