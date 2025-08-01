from abc import ABC, abstractmethod
from typing import List, NamedTuple
from uuid import UUID

from app.models import Chunk

__all__ = [
    "BaseIndex",
    "VectorSearchResult"
]


class VectorSearchResult(NamedTuple):
    """Result of a vector similarity search"""
    chunk: Chunk
    distance: float
    similarity: float


class BaseIndex(ABC):
    """Abstract base class for vector indexes"""
    
    def __init__(self, similarity_metric: str = "cosine"):
        """
        Initialize the index
        
        Args:
            similarity_metric: Type of similarity metric ('cosine', 'euclidean', 'dot_product')
        """
        self.similarity_metric = similarity_metric
        self._indexed_chunks: List[Chunk] = []
        self._is_built = False
    
    @abstractmethod
    def index(self, chunks: List[Chunk]) -> None:
        """
        Build the index from a list of chunks
        
        Args:
            chunks: List of chunks to index
        """
        pass
    
    @abstractmethod
    def search(self, query: List[float], k: int, similarity_metric: str = None) -> List[VectorSearchResult]:
        """
        Search for k most similar chunks to the query vector
        
        Args:
            query: Query vector
            k: Number of results to return
            similarity_metric: Override the default similarity metric for this search
            
        Returns:
            List of VectorSearchResult objects
        """
        pass
    
    @abstractmethod
    def add_chunk(self, chunk: Chunk) -> None:
        """
        Add a single chunk to the index
        
        Args:
            chunk: Chunk to add
        """
        pass
    
    @abstractmethod
    def remove_chunk(self, chunk_id: UUID) -> None:
        """
        Remove a chunk from the index
        
        Args:
            chunk_id: ID of the chunk to remove
        """
        pass
    
    @abstractmethod
    def get_chunk_by_id(self, chunk_id: UUID) -> Chunk:
        """
        Retrieve a chunk by its ID
        
        Args:
            chunk_id: ID of the chunk to retrieve
            
        Returns:
            The chunk if found, None otherwise
        """
        pass
    
    def _calculate_similarity(self, vec1: List[float], vec2: List[float], metric: str = None) -> tuple[float, float]:
        """
        Calculate similarity and distance between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector  
            metric: Similarity metric to use (defaults to self.similarity_metric)
            
        Returns:
            Tuple of (distance, similarity)
        """
        import numpy as np
        
        if metric is None:
            metric = self.similarity_metric
            
        # Convert to numpy arrays
        v1 = np.array(vec1, dtype=np.float32)
        v2 = np.array(vec2, dtype=np.float32)
        
        # Handle zero vectors
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 1.0, 0.0  # Max distance, min similarity
            
        if metric == "cosine":
            # Cosine similarity: dot(v1, v2) / (||v1|| * ||v2||)
            similarity = float(np.dot(v1, v2) / (norm1 * norm2))
            distance = 1.0 - similarity  # Convert to distance
            return distance, similarity
            
        elif metric == "euclidean":
            # Euclidean distance
            distance = float(np.linalg.norm(v1 - v2))
            # Convert distance to similarity (inverse relationship)
            similarity = 1.0 / (1.0 + distance)
            return distance, similarity
            
        elif metric == "dot_product":
            # Dot product (higher = more similar)
            similarity = float(np.dot(v1, v2))
            distance = -similarity  # Negative for sorting (lower distance = better)
            return distance, similarity
            
        else:
            raise ValueError(f"Unsupported similarity metric: {metric}")
    
    def is_built(self) -> bool:
        """Check if the index has been built"""
        return self._is_built
    
    def get_indexed_count(self) -> int:
        """Get the number of indexed chunks"""
        return len(self._indexed_chunks)
