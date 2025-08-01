import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from app.models import Library, CreateLibrary, UpdateLibrary
from app.models import Document, CreateDocument, UpdateDocument  
from app.models import Chunk, CreateChunk, UpdateChunk


class TestLibraryModels:
    """Test Library Pydantic models"""
    
    def test_create_library_valid(self):
        """Test creating a valid library"""
        create_data = CreateLibrary(
            name="Test Library",
            metadata={"description": "A test library"}
        )
        
        assert create_data.name == "Test Library"
        assert create_data.metadata["description"] == "A test library"
    
    def test_create_library_empty_name(self):
        """Test creating library with empty name fails"""
        with pytest.raises(ValidationError):
            CreateLibrary(name="", metadata={})
    
    def test_update_library_partial(self):
        """Test updating library with partial data"""
        update_data = UpdateLibrary(name="Updated Library")
        
        assert update_data.name == "Updated Library"
        assert update_data.metadata is None
    
    def test_library_full_model(self):
        """Test full Library model"""
        library = Library(
            name="Test Library",
            metadata={"key": "value"},
            documents=[]
        )
        
        assert library.id is not None
        assert library.name == "Test Library"
        assert library.created_at is not None
        assert len(library.documents) == 0


class TestDocumentModels:
    """Test Document Pydantic models"""
    
    def test_create_document_valid(self):
        """Test creating a valid document"""
        create_data = CreateDocument(
            title="Test Document",
            metadata={"author": "Test Author"}
        )
        
        assert create_data.title == "Test Document"
        assert create_data.metadata["author"] == "Test Author"
    
    def test_document_with_chunks(self):
        """Test document with chunks"""
        chunks = [
            Chunk(
                text="Test chunk",
                embedding=[0.1, 0.2, 0.3],
                metadata={}
            )
        ]
        
        document = Document(
            title="Test Document",
            chunks=chunks,
            metadata={}
        )
        
        assert len(document.chunks) == 1
        assert document.chunks[0].text == "Test chunk"


class TestChunkModels:
    """Test Chunk Pydantic models"""
    
    def test_create_chunk_valid(self):
        """Test creating a valid chunk"""
        create_data = CreateChunk(
            text="This is a test chunk",
            embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
            metadata={"position": 0}
        )
        
        assert create_data.text == "This is a test chunk"
        assert len(create_data.embedding) == 5
        assert create_data.metadata["position"] == 0
    
    def test_create_chunk_empty_text(self):
        """Test creating chunk with empty text fails"""
        with pytest.raises(ValidationError):
            CreateChunk(
                text="",
                embedding=[0.1, 0.2],
                metadata={}
            )
    
    def test_create_chunk_empty_embedding(self):
        """Test creating chunk with empty embedding fails"""
        with pytest.raises(ValidationError):
            CreateChunk(
                text="Test text",
                embedding=[],
                metadata={}
            )
    
    def test_update_chunk_partial(self):
        """Test updating chunk with partial data"""
        update_data = UpdateChunk(text="Updated text")
        
        assert update_data.text == "Updated text"
        assert update_data.embedding is None
        assert update_data.metadata is None