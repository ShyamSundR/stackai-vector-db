from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.repositories.library_repository import LibraryRepository
from app.core.dependencies import get_library_repository
from app.services.vector_index_service import VectorIndexService
from app.services.embedding_service import embedding_service

router = APIRouter()

# Global service instance
vector_service = VectorIndexService()


class SearchRequest(BaseModel):
    """Request model for similarity search"""
    query_embedding: Optional[List[float]] = Field(
        default=None,
        description="Query vector for similarity search. If not provided, query_text must be provided with auto_embed=True"
    )
    query_text: Optional[str] = Field(
        default=None,
        description="Query text to generate embedding for. Requires auto_embed=True and Cohere API key"
    )
    auto_embed: bool = Field(
        default=False,
        description="Whether to automatically generate embedding for query_text using Cohere API"
    )
    k: int = Field(default=5, ge=1, le=100, description="Number of similar chunks to return")
    similarity_metric: str = Field(default="cosine", description="Similarity metric to use")
    metadata_filter: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filter conditions")


class SearchResultItem(BaseModel):
    """Individual search result item"""
    chunk: Dict[str, Any]  # Chunk data
    distance: float
    similarity: float


class IndexResponse(BaseModel):
    """Response model for index operations"""
    status: str
    index_type: str
    message: Optional[str] = None


@router.post("/libraries/{library_id}/index", response_model=IndexResponse)
async def index_library(
    library_id: UUID,
    index_type: str = Query(default="brute_force", description="Type of index to build"),
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Build a vector index for a library"""
    # Check if library exists
    library = repo.get_library(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Get chunks for the library
    chunks = repo.get_library_chunks(library_id)
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks found for this library")
    
    try:
        # Set index type for the library
        vector_service.set_index_type(library_id, index_type)
        
        # Index the library
        result = await vector_service.index_library(library_id, chunks)
        
        return IndexResponse(
            status="indexed",
            index_type=index_type,
            message=f"Successfully indexed {len(chunks)} chunks"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index library: {str(e)}")


@router.post("/libraries/{library_id}/search")
async def search_similar_chunks(
    library_id: UUID,
    search_request: SearchRequest,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Search for similar chunks in a library"""
    # Check if library exists
    library = repo.get_library(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Handle query embedding generation
    query_embedding = search_request.query_embedding
    
    if query_embedding is None and search_request.query_text and search_request.auto_embed:
        # Generate embedding using Cohere API
        if not embedding_service.is_available():
            raise HTTPException(
                status_code=400,
                detail="Embedding service not available. Please provide query_embedding or configure Cohere API key."
            )
        
        try:
            query_embedding = await embedding_service.generate_query_embedding(search_request.query_text)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate query embedding: {str(e)}"
            )
    elif query_embedding is None:
        raise HTTPException(
            status_code=400,
            detail="Either provide query_embedding or set query_text with auto_embed=true"
        )
    
    try:
        # Perform search
        results = await vector_service.search_similar_chunks(
            library_id=library_id,
            query_embedding=query_embedding,
            k=search_request.k,
            similarity_metric=search_request.similarity_metric,
            metadata_filter=search_request.metadata_filter
        )
        
        # Convert VectorSearchResult objects to serializable format
        formatted_results = []
        for result in results:
            formatted_results.append({
                "chunk": {
                    "id": str(result.chunk.id),
                    "document_id": str(result.chunk.document_id),
                    "text": result.chunk.text,
                    "embedding": result.chunk.embedding,
                    "metadata": result.chunk.metadata,
                    "created_at": result.chunk.created_at.isoformat(),
                    "updated_at": result.chunk.updated_at.isoformat()
                },
                "distance": result.distance,
                "similarity": result.similarity
            })
        
        return {
            "query_info": {
                "k": search_request.k,
                "similarity_metric": search_request.similarity_metric,
                "metadata_filter": search_request.metadata_filter,
                "used_auto_embed": search_request.auto_embed and search_request.query_text is not None
            },
            "results": formatted_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/libraries/{library_id}/index_type")
async def get_index_type(
    library_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Get the current index type for a library"""
    # Check if library exists
    library = repo.get_library(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    index_type = vector_service.get_index_type(library_id)
    return {"library_id": library_id, "index_type": index_type}


@router.post("/libraries/{library_id}/index_type", response_model=IndexResponse)
async def set_index_type(
    library_id: UUID,
    index_type: str = Query(..., description="Index type to set"),
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Set the index type for a library"""
    # Check if library exists
    library = repo.get_library(library_id)
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    try:
        vector_service.set_index_type(library_id, index_type)
        return IndexResponse(
            status="index type set",
            index_type=index_type,
            message=f"Index type changed to {index_type}. You may need to rebuild the index."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/embedding/status")
async def get_embedding_status():
    """Get the status of the embedding service"""
    return {
        "embedding_service_available": embedding_service.is_available(),
        "cohere_configured": embedding_service.client is not None,
        "model": "embed-english-v3.0" if embedding_service.is_available() else None
    }