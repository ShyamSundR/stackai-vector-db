import threading
from typing import List
from uuid import UUID

from app.indexes.base import BaseIndex, VectorSearchResult
from app.models import Chunk


class BruteForceIndex(BaseIndex):
    """Brute-force vector index implementation using linear scan"""
    
    def __init__(self, similarity_metric: str = "cosine"):
        """
        Initialize brute-force index
        
        Args:
            similarity_metric: Type of similarity metric ('cosine', 'euclidean', 'dot_product')
        """
        super().__init__(similarity_metric)
        self._lock = threading.RLock()
    
    def index(self, chunks: List[Chunk]) -> None:
        """
        Build the index from a list of chunks
        
        Args:
            chunks: List of chunks to index
        """
        with self._lock:
            self._indexed_chunks = chunks.copy()
            self._is_built = True
    
    def search(self, query: List[float], k: int, similarity_metric: str = None) -> List[VectorSearchResult]:
        """
        Search for k most similar chunks using linear scan
        
        Args:
            query: Query vector
            k: Number of results to return
            similarity_metric: Override the default similarity metric for this search
            
        Returns:
            List of VectorSearchResult objects ordered by similarity (best first)
        """
        with self._lock:
            if not self._is_built or not self._indexed_chunks:
                return []
            
            if not query:
                raise ValueError("Query vector cannot be empty")
            
            # Limit k to available chunks
            k = min(k, len(self._indexed_chunks))
            if k <= 0:
                return []
            
            # Calculate similarities for all chunks
            results = []
            for chunk in self._indexed_chunks:
                try:
                    distance, similarity = self._calculate_similarity(query, chunk.embedding, similarity_metric)
                    results.append(VectorSearchResult(
                        chunk=chunk,
                        distance=distance,
                        similarity=similarity
                    ))
                except Exception as e:
                    # Skip chunks with incompatible embeddings
                    continue
            
            # Sort by distance (ascending) and take top k
            results.sort(key=lambda x: x.distance)
            return results[:k]
    
    def add_chunk(self, chunk: Chunk) -> None:
        """
        Add a single chunk to the index
        
        Args:
            chunk: Chunk to add
        """
        with self._lock:
            if chunk not in self._indexed_chunks:
                self._indexed_chunks.append(chunk)
                self._is_built = True
    
    def remove_chunk(self, chunk_id: UUID) -> None:
        """
        Remove a chunk from the index
        
        Args:
            chunk_id: ID of the chunk to remove
        """
        with self._lock:
            self._indexed_chunks = [chunk for chunk in self._indexed_chunks if chunk.id != chunk_id]
    
    def get_chunk_by_id(self, chunk_id: UUID) -> Chunk:
        """
        Retrieve a chunk by its ID
        
        Args:
            chunk_id: ID of the chunk to retrieve
            
        Returns:
            The chunk if found, None otherwise
        """
        with self._lock:
            for chunk in self._indexed_chunks:
                if chunk.id == chunk_id:
                    return chunk
            return None 