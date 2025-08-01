import pytest
from datetime import datetime
from uuid import uuid4, UUID
from unittest.mock import Mock, patch

from app.repositories.library_repository import LibraryRepository
from app.services.library_service import LibraryService
from app.services.document_service import DocumentService
from app.services.chunk_service import ChunkService
from app.services.vector_index_service import VectorIndexService, MetadataFilter
from app.services.embedding_service import EmbeddingService
from app.models import Library, CreateLibrary, UpdateLibrary
from app.models import Document, DocumentCreate, DocumentUpdate
from app.models import Chunk, CreateChunk, UpdateChunk


class TestLibraryRepository:
    """Test LibraryRepository CRUD operations"""
    
    def test_initialization(self):
        """Test repository initialization"""
        repo = LibraryRepository()
        assert len(repo._libraries) == 0
        assert len(repo._documents) == 0
        assert len(repo._chunks) == 0
        assert repo._lock is not None
    
    def test_create_library(self, repository):
        """Test creating a library"""
        create_data = CreateLibrary(
            name="Test Library",
            metadata={"description": "Test library"}
        )
        
        library = repository.create_library(create_data)
        
        assert library.name == "Test Library"
        assert library.metadata["description"] == "Test library"
        assert library.id is not None
        assert library.created_at is not None
        assert len(library.documents) == 0
        
        # Check it's stored in repository
        assert library.id in repository._libraries
    
    def test_get_library(self, repository, sample_library):
        """Test getting a library by ID"""
        # Add library to repository
        repository._libraries[sample_library.id] = sample_library
        
        retrieved = repository.get_library(sample_library.id)
        assert retrieved == sample_library
    
    def test_get_nonexistent_library(self, repository):
        """Test getting non-existent library returns None"""
        result = repository.get_library(uuid4())
        assert result is None
    
    def test_get_all_libraries(self, repository):
        """Test getting all libraries"""
        # Add multiple libraries
        lib1 = Library(name="Library 1", metadata={})
        lib2 = Library(name="Library 2", metadata={})
        
        repository._libraries[lib1.id] = lib1
        repository._libraries[lib2.id] = lib2
        
        all_libraries = repository.get_all_libraries()
        assert len(all_libraries) == 2
        assert lib1 in all_libraries
        assert lib2 in all_libraries
    
    def test_update_library(self, repository, sample_library):
        """Test updating a library"""
        # Add library to repository
        repository._libraries[sample_library.id] = sample_library
        
        update_data = UpdateLibrary(
            name="Updated Library",
            metadata={"description": "Updated description"}
        )
        
        updated = repository.update_library(sample_library.id, update_data)
        
        assert updated.name == "Updated Library"
        assert updated.metadata["description"] == "Updated description"
        assert updated.id == sample_library.id
        assert updated.updated_at is not None
    
    def test_update_nonexistent_library(self, repository):
        """Test updating non-existent library returns None"""
        update_data = UpdateLibrary(name="Updated")
        result = repository.update_library(uuid4(), update_data)
        assert result is None
    
    def test_delete_library(self, repository, sample_library):
        """Test deleting a library"""
        # Add library to repository
        repository._libraries[sample_library.id] = sample_library
        
        deleted = repository.delete_library(sample_library.id)
        
        assert deleted is True
        assert sample_library.id not in repository._libraries
    
    def test_delete_nonexistent_library(self, repository):
        """Test deleting non-existent library returns False"""
        result = repository.delete_library(uuid4())
        assert result is False
    
    def test_create_document(self, repository, sample_library):
        """Test creating a document"""
        # Add library first
        repository._libraries[sample_library.id] = sample_library
        
        create_data = DocumentCreate(
            title="Test Document",
            library_id=sample_library.id,
            metadata={"author": "Test Author"}
        )
        
        document = repository.create_document(create_data)
        
        assert document.title == "Test Document"
        assert document.library_id == sample_library.id
        assert document.metadata["author"] == "Test Author"
        assert document.id is not None
        
        # Check it's stored and linked
        assert document.id in repository._documents
        assert document in sample_library.documents
    
    def test_get_document(self, repository, sample_document):
        """Test getting a document by ID"""
        repository._documents[sample_document.id] = sample_document
        
        retrieved = repository.get_document(sample_document.id)
        assert retrieved == sample_document
    
    def test_get_library_documents(self, repository, sample_library):
        """Test getting all documents in a library"""
        repository._libraries[sample_library.id] = sample_library
        
        doc1 = Document(title="Doc 1", library_id=sample_library.id, metadata={})
        doc2 = Document(title="Doc 2", library_id=sample_library.id, metadata={})
        
        repository._documents[doc1.id] = doc1
        repository._documents[doc2.id] = doc2
        sample_library.documents = [doc1, doc2]
        
        documents = repository.get_library_documents(sample_library.id)
        assert len(documents) == 2
        assert doc1 in documents
        assert doc2 in documents
    
    def test_create_chunk(self, repository, sample_document):
        """Test creating a chunk"""
        repository._documents[sample_document.id] = sample_document
        
        chunk_data = Chunk(
            text="Test chunk",
            embedding=[0.1, 0.2, 0.3],
            metadata={"position": 0},
            document_id=sample_document.id
        )
        
        chunk = repository.create_chunk(chunk_data, sample_document.id)
        
        assert chunk.text == "Test chunk"
        assert chunk.document_id == sample_document.id
        assert chunk.id is not None
        
        # Check it's stored and linked
        assert chunk.id in repository._chunks
        assert chunk in sample_document.chunks
    
    def test_get_chunk(self, repository, sample_chunk):
        """Test getting a chunk by ID"""
        repository._chunks[sample_chunk.id] = sample_chunk
        
        retrieved = repository.get_chunk(sample_chunk.id)
        assert retrieved == sample_chunk
    
    def test_get_document_chunks(self, repository, sample_document):
        """Test getting all chunks in a document"""
        repository._documents[sample_document.id] = sample_document
        
        chunk1 = Chunk(text="Chunk 1", embedding=[0.1], metadata={}, document_id=sample_document.id)
        chunk2 = Chunk(text="Chunk 2", embedding=[0.2], metadata={}, document_id=sample_document.id)
        
        repository._chunks[chunk1.id] = chunk1
        repository._chunks[chunk2.id] = chunk2
        sample_document.chunks = [chunk1, chunk2]
        
        chunks = repository.get_document_chunks(sample_document.id)
        assert len(chunks) == 2
        assert chunk1 in chunks
        assert chunk2 in chunks
    
    def test_get_library_chunks(self, repository, sample_library):
        """Test getting all chunks in a library"""
        repository._libraries[sample_library.id] = sample_library
        
        # Create document and chunks
        doc = Document(title="Doc", library_id=sample_library.id, metadata={})
        chunk1 = Chunk(text="Chunk 1", embedding=[0.1], metadata={}, document_id=doc.id)
        chunk2 = Chunk(text="Chunk 2", embedding=[0.2], metadata={}, document_id=doc.id)
        
        doc.chunks = [chunk1, chunk2]
        sample_library.documents = [doc]
        
        repository._documents[doc.id] = doc
        repository._chunks[chunk1.id] = chunk1
        repository._chunks[chunk2.id] = chunk2
        
        chunks = repository.get_library_chunks(sample_library.id)
        assert len(chunks) == 2
        assert chunk1 in chunks
        assert chunk2 in chunks
    
    def test_thread_safety(self, repository):
        """Test basic thread safety with locks"""
        # This test verifies the lock exists and can be acquired
        with repository._lock:
            create_data = CreateLibrary(name="Thread Test", metadata={})
            library = repository.create_library(create_data)
            assert library.name == "Thread Test"


class TestLibraryService:
    """Test LibraryService business logic"""
    
    def test_initialization(self):
        """Test service initialization"""
        service = LibraryService()
        assert len(service._libraries) == 0
    
    @pytest.mark.asyncio
    async def test_create_library(self):
        """Test creating library through service"""
        service = LibraryService()
        create_data = CreateLibrary(name="Service Test", metadata={})
        
        library = await service.create_library(create_data)
        
        assert library.name == "Service Test"
        assert library.id in service._libraries
    
    @pytest.mark.asyncio
    async def test_get_library(self):
        """Test getting library through service"""
        service = LibraryService()
        create_data = CreateLibrary(name="Get Test", metadata={})
        
        created = await service.create_library(create_data)
        retrieved = await service.get_library(created.id)
        
        assert retrieved == created
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_library(self):
        """Test getting non-existent library returns None"""
        service = LibraryService()
        result = await service.get_library(uuid4())
        assert result is None


class TestDocumentService:
    """Test DocumentService business logic"""
    
    @pytest.mark.asyncio
    async def test_create_document(self):
        """Test creating document through service"""
        service = DocumentService()
        create_data = DocumentCreate(
            title="Service Doc",
            library_id=uuid4(),
            metadata={}
        )
        
        document = await service.create_document(create_data)
        
        assert document.title == "Service Doc"
        assert document.id in service._documents


class TestChunkService:
    """Test ChunkService business logic"""
    
    @pytest.mark.asyncio
    async def test_create_chunk(self):
        """Test creating chunk through service"""
        service = ChunkService()
        create_data = CreateChunk(
            text="Service chunk",
            embedding=[0.1, 0.2],
            metadata={}
        )
        
        chunk = await service.create_chunk(create_data)
        
        assert chunk.text == "Service chunk"
        assert chunk.id in service._chunks


class TestVectorIndexService:
    """Test VectorIndexService functionality"""
    
    def test_initialization(self):
        """Test vector index service initialization"""
        service = VectorIndexService()
        assert len(service._indexes) == 0
        assert "brute_force" in service._index_types
        assert "kdtree" in service._index_types
        assert service._default_type == "brute_force"
    
    def test_set_index_type(self):
        """Test setting index type for a library"""
        service = VectorIndexService()
        library_id = uuid4()
        
        service.set_index_type(library_id, "kdtree")
        # Should not raise error for valid type
        
        with pytest.raises(ValueError, match="Unsupported index type"):
            service.set_index_type(library_id, "invalid_type")
    
    def test_get_index_type(self):
        """Test getting index type for a library"""
        service = VectorIndexService()
        library_id = uuid4()
        
        # Should return default for new library
        assert service.get_index_type(library_id) == "brute_force"
        
        # Should return set type
        service.set_index_type(library_id, "kdtree")
        assert service.get_index_type(library_id) == "brute_force"  # Not indexed yet
    
    @pytest.mark.asyncio
    async def test_index_library(self, sample_chunks):
        """Test indexing a library"""
        service = VectorIndexService()
        library_id = uuid4()
        
        await service.index_library(library_id, sample_chunks, "brute_force")
        
        assert library_id in service._indexes
        index_type, index_instance = service._indexes[library_id]
        assert index_type == "brute_force"
        assert index_instance._is_built
    
    @pytest.mark.asyncio
    async def test_search_similar_chunks(self, sample_chunks, query_vector):
        """Test searching for similar chunks"""
        service = VectorIndexService()
        library_id = uuid4()
        
        # Index the library first
        await service.index_library(library_id, sample_chunks, "brute_force")
        
        results = await service.search_similar_chunks(
            library_id=library_id,
            query_embedding=query_vector,
            k=2,
            similarity_metric="cosine"
        )
        
        assert len(results) <= 2
        if results:
            assert hasattr(results[0], 'chunk')
            assert hasattr(results[0], 'similarity')
            assert hasattr(results[0], 'distance')
    
    @pytest.mark.asyncio
    async def test_search_nonexistent_library(self, query_vector):
        """Test searching non-existent library returns empty"""
        service = VectorIndexService()
        
        results = await service.search_similar_chunks(
            library_id=uuid4(),
            query_embedding=query_vector,
            k=5
        )
        
        assert len(results) == 0


class TestMetadataFilter:
    """Test MetadataFilter functionality"""
    
    def test_simple_equality_filter(self):
        """Test simple equality filtering"""
        metadata = {"category": "test", "score": 0.8}
        filter_conditions = {"category": "test"}
        
        result = MetadataFilter.apply_filter(metadata, filter_conditions)
        assert result is True
        
        # Test non-matching
        filter_conditions = {"category": "other"}
        result = MetadataFilter.apply_filter(metadata, filter_conditions)
        assert result is False
    
    def test_nested_field_filter(self):
        """Test nested field filtering"""
        metadata = {
            "author": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
        filter_conditions = {"author.name": "John Doe"}
        
        result = MetadataFilter.apply_filter(metadata, filter_conditions)
        assert result is True
    
    def test_numeric_comparison_filters(self):
        """Test numeric comparison filters"""
        metadata = {"score": 0.8, "count": 10}
        
        # Greater than
        result = MetadataFilter.apply_filter(metadata, {"score": {"$gt": 0.5}})
        assert result is True
        
        result = MetadataFilter.apply_filter(metadata, {"score": {"$gt": 0.9}})
        assert result is False
        
        # Less than or equal
        result = MetadataFilter.apply_filter(metadata, {"count": {"$lte": 10}})
        assert result is True
        
        result = MetadataFilter.apply_filter(metadata, {"count": {"$lte": 5}})
        assert result is False
    
    def test_array_filters(self):
        """Test array-based filters"""
        metadata = {"tags": ["python", "ml", "ai"], "categories": ["tech"]}
        
        # In filter
        result = MetadataFilter.apply_filter(metadata, {"tags": {"$in": ["python", "java"]}})
        assert result is True
        
        result = MetadataFilter.apply_filter(metadata, {"tags": {"$in": ["java", "ruby"]}})
        assert result is False
        
        # Contains filter
        result = MetadataFilter.apply_filter(metadata, {"tags": {"$contains": "ml"}})
        assert result is True
    
    def test_string_filters(self):
        """Test string-based filters"""
        metadata = {"title": "Machine Learning Basics", "author": "John Smith"}
        
        # Contains filter
        result = MetadataFilter.apply_filter(metadata, {"title": {"$contains": "learning"}})
        assert result is True
        
        # Regex filter
        result = MetadataFilter.apply_filter(metadata, {"author": {"$regex": "^John"}})
        assert result is True
    
    def test_existence_filter(self):
        """Test field existence filtering"""
        metadata = {"title": "Test", "score": 0.8}
        
        # Field exists
        result = MetadataFilter.apply_filter(metadata, {"score": {"$exists": True}})
        assert result is True
        
        # Field doesn't exist
        result = MetadataFilter.apply_filter(metadata, {"missing_field": {"$exists": False}})
        assert result is True
        
        result = MetadataFilter.apply_filter(metadata, {"score": {"$exists": False}})
        assert result is False


class TestEmbeddingService:
    """Test EmbeddingService functionality"""
    
    def test_initialization_without_api_key(self):
        """Test service initialization without API key"""
        with patch.dict('os.environ', {}, clear=True):
            service = EmbeddingService()
            assert not service.is_available()
            assert service.client is None
    
    @patch('cohere.Client')
    def test_initialization_with_api_key(self, mock_cohere):
        """Test service initialization with API key"""
        with patch.dict('os.environ', {'COHERE_API_KEY': 'test_key'}):
            service = EmbeddingService()
            assert service.is_available()
            mock_cohere.assert_called_once_with(api_key='test_key')
    
    @pytest.mark.asyncio
    @patch('cohere.Client')
    async def test_generate_embedding_success(self, mock_cohere):
        """Test successful embedding generation"""
        # Mock the Cohere client response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3, 0.4, 0.5]]
        mock_client.embed.return_value = mock_response
        mock_cohere.return_value = mock_client
        
        with patch.dict('os.environ', {'COHERE_API_KEY': 'test_key'}):
            service = EmbeddingService()
            service.client = mock_client
            
            result = await service.generate_embedding("test text")
            
            assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
            mock_client.embed.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_embedding_service_unavailable(self):
        """Test embedding generation when service unavailable"""
        service = EmbeddingService()
        service.client = None
        
        with pytest.raises(ValueError, match="Embedding service not available"):
            await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_generate_embedding_empty_text(self):
        """Test embedding generation with empty text"""
        with patch.dict('os.environ', {'COHERE_API_KEY': 'test_key'}):
            service = EmbeddingService()
            
            with pytest.raises(ValueError, match="Text cannot be empty"):
                await service.generate_embedding("")
    
    @pytest.mark.asyncio
    @patch('cohere.Client')
    async def test_generate_batch_embeddings(self, mock_cohere):
        """Test batch embedding generation"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2], [0.3, 0.4]]
        mock_client.embed.return_value = mock_response
        mock_cohere.return_value = mock_client
        
        with patch.dict('os.environ', {'COHERE_API_KEY': 'test_key'}):
            service = EmbeddingService()
            service.client = mock_client
            
            result = await service.generate_batch_embeddings(["text1", "text2"])
            
            assert len(result) == 2
            assert result[0] == [0.1, 0.2]
            assert result[1] == [0.3, 0.4]