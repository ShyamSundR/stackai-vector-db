import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from app.models import Library, CreateLibrary, UpdateLibrary
from app.models import Document, DocumentCreate, DocumentUpdate  
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
        create_data = DocumentCreate(
            title="Test Document",
            library_id=uuid4(),
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
                metadata={},
                document_id=uuid4()
            )
        ]
        
        document = Document(
            title="Test Document",
            chunks=chunks,
            metadata={},
            library_id=uuid4()
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
    
    def test_create_chunk_with_auto_embed(self):
        """Test creating chunk with auto_embed flag"""
        create_data = CreateChunk(
            text="This is a test chunk",
            auto_embed=True,
            metadata={"position": 0}
        )
        
        assert create_data.text == "This is a test chunk"
        assert create_data.auto_embed is True
        assert create_data.embedding is None
    
    def test_update_chunk_partial(self):
        """Test updating chunk with partial data"""
        update_data = UpdateChunk(text="Updated text")
        
        assert update_data.text == "Updated text"
        assert update_data.embedding is None
        assert update_data.metadata is None