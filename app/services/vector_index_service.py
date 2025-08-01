import numpy as np
from uuid import UUID
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
from app.models import Chunk
from app.indexes.brute_force import BruteForceIndex
from app.indexes.kdtree import KDTreeIndex


class VectorSearchResult:
    """Result from vector similarity search"""
    def __init__(self, chunk: Chunk, distance: float, similarity: float):
        self.chunk = chunk
        self.distance = distance
        self.similarity = similarity


class MetadataFilter:
    """Advanced metadata filtering with support for various operations"""
    
    @staticmethod
    def apply_filter(chunk_metadata: Dict[str, Any], filter_conditions: Dict[str, Any]) -> bool:
        """Apply complex filter conditions to chunk metadata"""
        for key, condition in filter_conditions.items():
            if not MetadataFilter._evaluate_condition(chunk_metadata, key, condition):
                return False
        return True
    
    @staticmethod
    def _evaluate_condition(metadata: Dict[str, Any], key: str, condition: Any) -> bool:
        """Evaluate a single filter condition"""
        
        # Handle nested keys (e.g., "author.name")
        value = MetadataFilter._get_nested_value(metadata, key)
        
        # Simple equality check
        if not isinstance(condition, dict):
            return value == condition
        
        # Complex condition operations
        for op, expected in condition.items():
            if op == "$eq":  # Equal
                if value != expected:
                    return False
            elif op == "$ne":  # Not equal
                if value == expected:
                    return False
            elif op == "$gt":  # Greater than
                if not (value is not None and value > expected):
                    return False
            elif op == "$gte":  # Greater than or equal
                if not (value is not None and value >= expected):
                    return False
            elif op == "$lt":  # Less than
                if not (value is not None and value < expected):
                    return False
            elif op == "$lte":  # Less than or equal
                if not (value is not None and value <= expected):
                    return False
            elif op == "$in":  # In array
                if value not in expected:
                    return False
            elif op == "$nin":  # Not in array
                if value in expected:
                    return False
            elif op == "$contains":  # String contains
                if not (isinstance(value, str) and expected.lower() in value.lower()):
                    return False
            elif op == "$regex":  # Regular expression
                if not (isinstance(value, str) and re.search(expected, value, re.IGNORECASE)):
                    return False
            elif op == "$exists":  # Field exists
                field_exists = MetadataFilter._has_nested_key(metadata, key)
                if expected != field_exists:
                    return False
            elif op == "$date_after":  # Date after
                date_value = MetadataFilter._parse_date(value)
                expected_date = MetadataFilter._parse_date(expected)
                if not (date_value and expected_date and date_value > expected_date):
                    return False
            elif op == "$date_before":  # Date before
                date_value = MetadataFilter._parse_date(value)
                expected_date = MetadataFilter._parse_date(expected)
                if not (date_value and expected_date and date_value < expected_date):
                    return False
            elif op == "$date_range":  # Date in range
                date_value = MetadataFilter._parse_date(value)
                start_date = MetadataFilter._parse_date(expected.get("start"))
                end_date = MetadataFilter._parse_date(expected.get("end"))
                if not (date_value and start_date and end_date and start_date <= date_value <= end_date):
                    return False
            else:
                # Unknown operator - ignore or could raise error
                continue
                
        return True
    
    @staticmethod
    def _get_nested_value(metadata: Dict[str, Any], key: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = key.split('.')
        value = metadata
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        return value
    
    @staticmethod
    def _has_nested_key(metadata: Dict[str, Any], key: str) -> bool:
        """Check if nested key exists using dot notation"""
        keys = key.split('.')
        value = metadata
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return False
        return True
    
    @staticmethod
    def _parse_date(date_value: Any) -> Optional[datetime]:
        """Parse various date formats to datetime object"""
        if isinstance(date_value, datetime):
            return date_value
        elif isinstance(date_value, str):
            try:
                # Try ISO format first
                return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except:
                try:
                    # Try common formats
                    for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d', '%d/%m/%Y']:
                        try:
                            return datetime.strptime(date_value, fmt)
                        except:
                            continue
                except:
                    pass
        return None


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
        index_class = self._index_types[index_type]
        idx = index_class()
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
        """Search for similar chunks in a library's index with advanced metadata filtering"""
        if library_id not in self._indexes:
            return []
        
        _, idx = self._indexes[library_id]
        
        # Get initial results from vector search
        initial_k = k * 3 if metadata_filter else k  # Get more results for filtering
        results = idx.search(query_embedding, initial_k, similarity_metric)
        
        # Apply advanced metadata filtering if specified
        if metadata_filter:
            filtered_results = []
            for result in results:
                if MetadataFilter.apply_filter(result.chunk.metadata, metadata_filter):
                    filtered_results.append(result)
                    if len(filtered_results) >= k:  # Stop when we have enough results
                        break
            return filtered_results
        
        return results[:k]

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
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        magnitude_product = np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np)
        
        if magnitude_product == 0:
            return 0.0
        
        return dot_product / magnitude_product
    
    def _euclidean_distance(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate Euclidean distance between two vectors"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return float(np.linalg.norm(v1 - v2))        
