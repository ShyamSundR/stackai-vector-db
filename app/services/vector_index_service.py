import numpy as np
from uuid import UUID
from typing import Dict, List, Any, Optional
from app.models import Chunk
from app.indexes.brute_force import BruteForceIndex
from app.indexes.kdtree import KDTreeIndex
from app.indexes.base import VectorSearchResult


class VectorIndexService:
    """Service for managing vector indexes across libraries"""
    
    def __init__(self):
        self._indexes: dict[UUID, tuple[str, object]] = {}  # library_id -> (index_type, index_instance)
        self._index_types = {
            'brute_force': BruteForceIndex,
            'kdtree': KDTreeIndex
        }
        self._default_type = 'brute_force'
    
    def set_index_type(self, library_id: UUID, index_type: str) -> None:
        """Set the index type for a library"""
        if index_type not in self._index_types:
            raise ValueError(f"Unsupported index type: {index_type}. Available: {list(self._index_types.keys())}")
        
        # Clear existing index when changing type
        if library_id in self._indexes:
            del self._indexes[library_id]
    
    def get_index_type(self, library_id: UUID) -> str:
        """Get the current index type for a library"""
        if library_id in self._indexes:
            return self._indexes[library_id][0]
        return self._default_type
    
    async def index_library(self, library_id: UUID, chunks: List[Chunk], index_type: str = None) -> None:
        """Build/rebuild the vector index for a library"""
        if not index_type:
            index_type = self.get_index_type(library_id)
        
        if index_type not in self._index_types:
            raise ValueError(f"Unsupported index type: {index_type}")
        
        # Create new index instance
        idx = self._index_types[index_type]()
        idx.index(chunks)
        self._indexes[library_id] = (index_type, idx)

    async def search_similar_chunks(
        self, 
        library_id: UUID, 
        query_embedding: List[float], 
        k: int = 10,
        similarity_metric: str = "cosine",
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """Search for similar chunks in a library's index"""
        if library_id not in self._indexes:
            return []
        
        _, idx = self._indexes[library_id]
        results = idx.search(query_embedding, k, similarity_metric)
        
        # Apply metadata filtering if specified
        if metadata_filter:
            filtered_results = []
            for result in results:
                chunk_metadata = result.chunk.metadata
                # Check if all filter conditions match
                if all(chunk_metadata.get(key) == value for key, value in metadata_filter.items()):
                    filtered_results.append(result)
            return filtered_results
        
        return results

    async def add_chunk_to_index(self, library_id: UUID, chunk: Chunk) -> None:
        """Add a single chunk to the library's index"""
        if library_id not in self._indexes:
            # Default to brute_force if not set
            self._indexes[library_id] = (self._default_type, BruteForceIndex())
        
        _, idx = self._indexes[library_id]
        idx.add_chunk(chunk)

    async def remove_chunk_from_index(self, library_id: UUID, chunk_id: UUID) -> None:
        """Remove a chunk from the library's index"""
        if library_id in self._indexes:
            _, idx = self._indexes[library_id]
            idx.remove_chunk(chunk_id)
    
    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            return 0.0
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    
    def _euclidean_distance(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate Euclidean distance between two vectors"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return float(np.linalg.norm(v1 - v2))        
