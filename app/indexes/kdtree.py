import threading
from typing import List, Optional
from uuid import UUID

from app.indexes.base import BaseIndex, VectorSearchResult
from app.models import Chunk


class KDTreeNode:
    """Node in the KD-Tree"""
    
    def __init__(self, chunk: Chunk, axis: int):
        self.chunk = chunk
        self.axis = axis
        self.left: Optional['KDTreeNode'] = None
        self.right: Optional['KDTreeNode'] = None


class KDTreeIndex(BaseIndex):
    """KD-Tree vector index implementation for efficient nearest neighbor search"""
    
    def __init__(self, similarity_metric: str = "cosine"):
        """
        Initialize KD-Tree index
        
        Args:
            similarity_metric: Type of similarity metric ('cosine', 'euclidean', 'dot_product')
        """
        super().__init__(similarity_metric)
        self._root: Optional[KDTreeNode] = None
        self._lock = threading.RLock()
        self._dimensions = 0
    
    def index(self, chunks: List[Chunk]) -> None:
        """
        Build the KD-Tree from a list of chunks
        
        Args:
            chunks: List of chunks to index
        """
        with self._lock:
            if not chunks:
                self._root = None
                self._indexed_chunks = []
                self._is_built = True
                return
            
            # Determine dimensionality from first chunk
            self._dimensions = len(chunks[0].embedding)
            
            # Validate all chunks have same dimensionality
            for chunk in chunks:
                if len(chunk.embedding) != self._dimensions:
                    raise ValueError(f"Inconsistent embedding dimensions: expected {self._dimensions}, got {len(chunk.embedding)}")
            
            self._indexed_chunks = chunks.copy()
            self._root = self._build_tree(chunks, 0)
            self._is_built = True
    
    def _build_tree(self, chunks: List[Chunk], depth: int) -> Optional[KDTreeNode]:
        """Recursively build the KD-Tree"""
        if not chunks:
            return None
        
        # Choose axis based on depth
        axis = depth % self._dimensions
        
        # Sort chunks by the current axis
        chunks.sort(key=lambda chunk: chunk.embedding[axis])
        
        # Choose median as pivot
        median_idx = len(chunks) // 2
        median_chunk = chunks[median_idx]
        
        # Create node and recursively build subtrees
        node = KDTreeNode(median_chunk, axis)
        node.left = self._build_tree(chunks[:median_idx], depth + 1)
        node.right = self._build_tree(chunks[median_idx + 1:], depth + 1)
        
        return node
    
    def search(self, query: List[float], k: int, similarity_metric: str = None) -> List[VectorSearchResult]:
        """
        Search for k most similar chunks using KD-Tree
        
        Args:
            query: Query vector
            k: Number of results to return
            similarity_metric: Override the default similarity metric for this search
            
        Returns:
            List of VectorSearchResult objects ordered by similarity (best first)
        """
        with self._lock:
            if not self._is_built or not self._root:
                return []
            
            if not query:
                raise ValueError("Query vector cannot be empty")
            
            if len(query) != self._dimensions:
                raise ValueError(f"Query dimension mismatch: expected {self._dimensions}, got {len(query)}")
            
            # Limit k to available chunks
            k = min(k, len(self._indexed_chunks))
            if k <= 0:
                return []
            
            # Use a priority queue to maintain k best results
            best_results = []
            
            def search_node(node: Optional[KDTreeNode], depth: int):
                if node is None:
                    return
                
                # Calculate distance to current node
                try:
                    distance, similarity = self._calculate_similarity(query, node.chunk.embedding, similarity_metric)
                    
                    # Add to results if we have space or this is better than worst result
                    if len(best_results) < k:
                        best_results.append(VectorSearchResult(
                            chunk=node.chunk,
                            distance=distance,
                            similarity=similarity
                        ))
                        # Keep results sorted by distance (ascending)
                        best_results.sort(key=lambda x: x.distance)
                    elif distance < best_results[-1].distance:
                        # Replace worst result
                        best_results[-1] = VectorSearchResult(
                            chunk=node.chunk,
                            distance=distance,
                            similarity=similarity
                        )
                        # Re-sort to maintain order
                        best_results.sort(key=lambda x: x.distance)
                
                except Exception:
                    # Skip nodes with incompatible embeddings
                    pass
                
                # Decide which subtree to search first
                axis = node.axis
                diff = query[axis] - node.chunk.embedding[axis]
                
                if diff <= 0:
                    # Query point is to the left, search left first
                    search_node(node.left, depth + 1)
                    # Check if we need to search right subtree
                    if len(best_results) < k or abs(diff) < best_results[-1].distance:
                        search_node(node.right, depth + 1)
                else:
                    # Query point is to the right, search right first
                    search_node(node.right, depth + 1)
                    # Check if we need to search left subtree
                    if len(best_results) < k or abs(diff) < best_results[-1].distance:
                        search_node(node.left, depth + 1)
            
            search_node(self._root, 0)
            return best_results
    
    def add_chunk(self, chunk: Chunk) -> None:
        """
        Add a single chunk to the index
        Note: This requires rebuilding the tree for optimal performance
        
        Args:
            chunk: Chunk to add
        """
        with self._lock:
            if chunk not in self._indexed_chunks:
                self._indexed_chunks.append(chunk)
                # Rebuild tree with all chunks
                self.index(self._indexed_chunks)
    
    def remove_chunk(self, chunk_id: UUID) -> None:
        """
        Remove a chunk from the index
        Note: This requires rebuilding the tree
        
        Args:
            chunk_id: ID of the chunk to remove
        """
        with self._lock:
            self._indexed_chunks = [chunk for chunk in self._indexed_chunks if chunk.id != chunk_id]
            # Rebuild tree with remaining chunks
            self.index(self._indexed_chunks)
    
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
