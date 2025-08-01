import pytest
from datetime import datetime
from uuid import uuid4, UUID
from typing import List

from app.models import Library, Document, Chunk
from app.repositories import LibraryRepository
from app.indexes import BruteForceIndex, KDTreeIndex


@pytest.fixture
def sample_library() -> Library:
    """Create a sample library for testing"""
    return Library(
        id=uuid4(),
        name="Test Library",
        documents=[],
        metadata={"description": "A test library", "version": "1.0"},
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_document() -> Document:
    """Create a sample document for testing"""
    return Document(
        id=uuid4(),
        title="Test Document",
        chunks=[],
        metadata={"author": "Test Author", "pages": 10},
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_chunk() -> Chunk:
    """Create a sample chunk for testing"""
    return Chunk(
        id=uuid4(),
        text="This is a test chunk with some sample text content.",
        embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
        metadata={"position": 0, "length": 50},
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_chunks() -> List[Chunk]:
    """Create multiple sample chunks with different embeddings for testing"""
    chunks = []
    
    # Chunk 1: Similar to query [0.1, 0.2, 0.3, 0.4, 0.5]
    chunks.append(Chunk(
        id=uuid4(),
        text="First test chunk with similar content.",
        embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
        metadata={"position": 0},
        created_at=datetime.utcnow()
    ))
    
    # Chunk 2: Somewhat similar
    chunks.append(Chunk(
        id=uuid4(),
        text="Second test chunk with related content.",
        embedding=[0.2, 0.3, 0.4, 0.5, 0.6],
        metadata={"position": 1},
        created_at=datetime.utcnow()
    ))
    
    # Chunk 3: Different
    chunks.append(Chunk(
        id=uuid4(),
        text="Third test chunk with different content.",
        embedding=[0.8, 0.7, 0.6, 0.1, 0.2],
        metadata={"position": 2},
        created_at=datetime.utcnow()
    ))
    
    # Chunk 4: Very different
    chunks.append(Chunk(
        id=uuid4(),
        text="Fourth test chunk with very different content.",
        embedding=[-0.5, -0.4, -0.3, -0.2, -0.1],
        metadata={"position": 3},
        created_at=datetime.utcnow()
    ))
    
    return chunks


@pytest.fixture
def repository() -> LibraryRepository:
    """Create a fresh repository for testing"""
    return LibraryRepository()


@pytest.fixture
def brute_force_index() -> BruteForceIndex:
    """Create a brute force index for testing"""
    return BruteForceIndex(similarity_metric="cosine")


@pytest.fixture
def kdtree_index() -> KDTreeIndex:
    """Create a KD-tree index for testing"""
    return KDTreeIndex(similarity_metric="cosine")


@pytest.fixture
def query_vector() -> List[float]:
    """Sample query vector for testing"""
    return [0.1, 0.2, 0.3, 0.4, 0.5]