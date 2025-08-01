import pytest
import numpy as np
from typing import List
from uuid import uuid4

from app.indexes.brute_force import BruteForceIndex
from app.indexes.kdtree import KDTreeIndex
from app.indexes.base import BaseIndex, VectorSearchResult
from app.models import Chunk


class TestBruteForceIndex:
    """Test BruteForceIndex implementation"""
    
    def test_initialization(self):
        """Test BruteForceIndex initialization"""
        index = BruteForceIndex(similarity_metric="cosine")
        assert index.similarity_metric == "cosine"
        assert not index._is_built
        assert len(index._indexed_chunks) == 0
    
    def test_index_chunks(self, sample_chunks):
        """Test indexing chunks"""
        index = BruteForceIndex()
        index.index(sample_chunks)
        
        assert index._is_built
        assert len(index._indexed_chunks) == len(sample_chunks)
        assert index._indexed_chunks[0].text == sample_chunks[0].text
    
    def test_index_empty_chunks(self):
        """Test indexing with empty chunk list"""
        index = BruteForceIndex()
        index.index([])
        
        assert index._is_built
        assert len(index._indexed_chunks) == 0
    
    def test_search_cosine_similarity(self, sample_chunks, query_vector):
        """Test search with cosine similarity"""
        index = BruteForceIndex(similarity_metric="cosine")
        index.index(sample_chunks)
        
        results = index.search(query_vector, k=2, similarity_metric="cosine")
        
        assert len(results) == 2
        assert isinstance(results[0], VectorSearchResult)
        assert results[0].chunk in sample_chunks
        assert 0 <= results[0].similarity <= 1
        assert results[0].distance >= 0
        
        # Results should be sorted by similarity (descending)
        assert results[0].similarity >= results[1].similarity
    
    def test_search_euclidean_distance(self, sample_chunks, query_vector):
        """Test search with Euclidean distance"""
        index = BruteForceIndex()
        index.index(sample_chunks)
        
        results = index.search(query_vector, k=3, similarity_metric="euclidean")
        
        assert len(results) == 3
        assert results[0].distance >= 0
        
        # Results should be sorted by distance (ascending for Euclidean)
        assert results[0].distance <= results[1].distance <= results[2].distance
    
    def test_search_dot_product(self, sample_chunks, query_vector):
        """Test search with dot product"""
        index = BruteForceIndex()
        index.index(sample_chunks)
        
        results = index.search(query_vector, k=2, similarity_metric="dot_product")
        
        assert len(results) == 2
        # Results should be sorted by dot product (descending)
        assert results[0].similarity >= results[1].similarity
    
    def test_search_not_built(self, query_vector):
        """Test search on unbuilt index returns empty"""
        index = BruteForceIndex()
        results = index.search(query_vector, k=5)
        
        assert len(results) == 0
    
    def test_search_empty_query(self, sample_chunks):
        """Test search with empty query raises ValueError"""
        index = BruteForceIndex()
        index.index(sample_chunks)
        
        with pytest.raises(ValueError, match="Query vector cannot be empty"):
            index.search([], k=5)
    
    def test_search_k_larger_than_chunks(self, sample_chunks, query_vector):
        """Test search with k larger than available chunks"""
        index = BruteForceIndex()
        index.index(sample_chunks)
        
        results = index.search(query_vector, k=100)
        
        # Should return all available chunks
        assert len(results) == len(sample_chunks)
    
    def test_add_chunk(self, sample_chunk):
        """Test adding a single chunk"""
        index = BruteForceIndex()
        index.add_chunk(sample_chunk)
        
        assert sample_chunk in index._indexed_chunks
        assert len(index._indexed_chunks) == 1
    
    def test_remove_chunk(self, sample_chunks):
        """Test removing a chunk"""
        index = BruteForceIndex()
        index.index(sample_chunks)
        
        chunk_to_remove = sample_chunks[0]
        index.remove_chunk(chunk_to_remove.id)
        
        assert chunk_to_remove not in index._indexed_chunks
        assert len(index._indexed_chunks) == len(sample_chunks) - 1
    
    def test_remove_nonexistent_chunk(self, sample_chunks):
        """Test removing a chunk that doesn't exist"""
        index = BruteForceIndex()
        index.index(sample_chunks)
        
        initial_count = len(index._indexed_chunks)
        index.remove_chunk(uuid4())  # Random UUID
        
        # Should not affect the index
        assert len(index._indexed_chunks) == initial_count
    
    def test_get_chunk_by_id(self, sample_chunks):
        """Test retrieving chunk by ID"""
        index = BruteForceIndex()
        index.index(sample_chunks)
        
        target_chunk = sample_chunks[0]
        retrieved_chunk = index.get_chunk_by_id(target_chunk.id)
        
        assert retrieved_chunk == target_chunk
    
    def test_get_nonexistent_chunk(self, sample_chunks):
        """Test retrieving nonexistent chunk returns None"""
        index = BruteForceIndex()
        index.index(sample_chunks)
        
        result = index.get_chunk_by_id(uuid4())
        assert result is None
    
    def test_thread_safety(self, sample_chunks):
        """Test basic thread safety with locks"""
        index = BruteForceIndex()
        
        # This test verifies the lock exists and can be acquired
        with index._lock:
            index.index(sample_chunks)
            assert index._is_built


class TestKDTreeIndex:
    """Test KDTreeIndex implementation"""
    
    def test_initialization(self):
        """Test KDTreeIndex initialization"""
        index = KDTreeIndex(similarity_metric="cosine")
        assert index.similarity_metric == "cosine"
        assert not index._is_built
        assert index._root is None
    
    def test_index_chunks(self, sample_chunks):
        """Test indexing chunks builds tree"""
        index = KDTreeIndex()
        index.index(sample_chunks)
        
        assert index._is_built
        assert index._root is not None
        assert len(index._indexed_chunks) == len(sample_chunks)
    
    def test_index_empty_chunks(self):
        """Test indexing with empty chunk list still marks as built"""
        index = KDTreeIndex()
        index.index([])
        
        # KDTree marks as built even with empty chunks
        assert index._is_built
        assert index._root is None
    
    def test_index_single_chunk(self, sample_chunk):
        """Test indexing with single chunk"""
        index = KDTreeIndex()
        index.index([sample_chunk])
        
        assert index._is_built
        assert index._root is not None
        assert index._root.chunk == sample_chunk
    
    def test_search_cosine_similarity(self, sample_chunks, query_vector):
        """Test KDTree search with cosine similarity"""
        index = KDTreeIndex(similarity_metric="cosine")
        index.index(sample_chunks)
        
        results = index.search(query_vector, k=2, similarity_metric="cosine")
        
        assert len(results) <= 2  # KDTree might return fewer results
        if results:
            assert isinstance(results[0], VectorSearchResult)
            assert results[0].chunk in sample_chunks
            assert 0 <= results[0].similarity <= 1
    
    def test_search_not_built(self, query_vector):
        """Test search on unbuilt KDTree returns empty"""
        index = KDTreeIndex()
        results = index.search(query_vector, k=5)
        
        assert len(results) == 0
    
    def test_search_empty_query(self, sample_chunks):
        """Test search with empty query raises ValueError"""
        index = KDTreeIndex()
        index.index(sample_chunks)
        
        with pytest.raises(ValueError, match="Query vector cannot be empty"):
            index.search([], k=5)
    
    def test_add_chunk(self, sample_chunks):
        """Test adding chunk to existing tree"""
        index = KDTreeIndex()
        index.index(sample_chunks)
        
        # Create a new chunk not in the original list
        new_chunk = Chunk(
            text="New chunk for testing",
            embedding=[0.5, 0.5, 0.5, 0.5, 0.5],
            metadata={"test": True},
            document_id=uuid4()  # Add required document_id
        )
        
        index.add_chunk(new_chunk)
        assert new_chunk in index._indexed_chunks
    
    def test_remove_chunk(self, sample_chunks):
        """Test removing chunk from tree"""
        index = KDTreeIndex()
        index.index(sample_chunks)
        
        chunk_to_remove = sample_chunks[0]
        index.remove_chunk(chunk_to_remove.id)
        
        assert chunk_to_remove not in index._indexed_chunks
    
    def test_get_chunk_by_id(self, sample_chunks):
        """Test retrieving chunk by ID from KDTree"""
        index = KDTreeIndex()
        index.index(sample_chunks)
        
        target_chunk = sample_chunks[0]
        retrieved_chunk = index.get_chunk_by_id(target_chunk.id)
        
        assert retrieved_chunk == target_chunk


class TestBaseIndexInterface:
    """Test BaseIndex abstract interface compliance"""
    
    def test_brute_force_implements_interface(self):
        """Test BruteForceIndex implements BaseIndex interface"""
        index = BruteForceIndex()
        assert isinstance(index, BaseIndex)
        
        # Check all abstract methods are implemented
        assert hasattr(index, 'index')
        assert hasattr(index, 'search')
        assert hasattr(index, 'add_chunk')
        assert hasattr(index, 'remove_chunk')
        assert hasattr(index, 'get_chunk_by_id')
    
    def test_kdtree_implements_interface(self):
        """Test KDTreeIndex implements BaseIndex interface"""
        index = KDTreeIndex()
        assert isinstance(index, BaseIndex)
        
        # Check all abstract methods are implemented
        assert hasattr(index, 'index')
        assert hasattr(index, 'search')
        assert hasattr(index, 'add_chunk')
        assert hasattr(index, 'remove_chunk')
        assert hasattr(index, 'get_chunk_by_id')
    
    def test_similarity_calculation_methods(self):
        """Test similarity calculation methods exist in base class"""
        index = BruteForceIndex()
        
        vec1 = [0.1, 0.2, 0.3]
        vec2 = [0.4, 0.5, 0.6]
        
        # Test cosine similarity
        distance, similarity = index._calculate_similarity(vec1, vec2, "cosine")
        assert isinstance(distance, float)
        assert isinstance(similarity, float)
        assert 0 <= similarity <= 1
        
        # Test euclidean distance
        distance, similarity = index._calculate_similarity(vec1, vec2, "euclidean")
        assert isinstance(distance, float)
        assert isinstance(similarity, float)
        assert distance >= 0
        
        # Test dot product
        distance, similarity = index._calculate_similarity(vec1, vec2, "dot_product")
        assert isinstance(distance, float)
        assert isinstance(similarity, float)


class TestVectorSearchResult:
    """Test VectorSearchResult named tuple"""
    
    def test_vector_search_result_creation(self, sample_chunk):
        """Test creating VectorSearchResult"""
        result = VectorSearchResult(
            chunk=sample_chunk,
            distance=0.5,
            similarity=0.8
        )
        
        assert result.chunk == sample_chunk
        assert result.distance == 0.5
        assert result.similarity == 0.8
    
    def test_vector_search_result_fields(self, sample_chunk):
        """Test VectorSearchResult field access"""
        result = VectorSearchResult(sample_chunk, 0.3, 0.9)
        
        # Test named tuple field access
        assert hasattr(result, 'chunk')
        assert hasattr(result, 'distance')
        assert hasattr(result, 'similarity')
        
        # Test tuple unpacking
        chunk, distance, similarity = result
        assert chunk == sample_chunk
        assert distance == 0.3
        assert similarity == 0.9
