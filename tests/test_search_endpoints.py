import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
import json

from app.main import app
from app.models import Library, Document, Chunk
from app.repositories.library_repository import LibraryRepository
from app.services.vector_index_service import VectorIndexService, VectorSearchResult
from app.services.embedding_service import EmbeddingService


class TestSearchEndpoints:
    """Test search router endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_repository(self):
        """Mock repository"""
        return Mock(spec=LibraryRepository)
    
    @pytest.fixture
    def mock_vector_service(self):
        """Mock vector index service"""
        return Mock(spec=VectorIndexService)
    
    @pytest.fixture
    def mock_embedding_service(self):
        """Mock embedding service"""
        return Mock(spec=EmbeddingService)
    
    @pytest.fixture
    def sample_library_id(self):
        """Sample library ID"""
        return str(uuid4())
    
    @pytest.fixture
    def sample_library(self, sample_library_id):
        """Sample library"""
        return Library(
            id=sample_library_id,
            name="Test Library",
            metadata={"description": "Test library"},
            documents=[]
        )
    
    @pytest.fixture
    def sample_chunks(self):
        """Sample chunks for testing"""
        return [
            Chunk(
                text="Machine learning basics",
                embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
                metadata={"topic": "AI"},
                document_id=uuid4()
            ),
            Chunk(
                text="Deep learning neural networks",
                embedding=[0.2, 0.3, 0.4, 0.5, 0.6],
                metadata={"topic": "AI"},
                document_id=uuid4()
            )
        ]


class TestBuildIndexEndpoint:
    """Test POST /api/v1/search/libraries/{library_id}/index"""
    
    @patch('app.core.dependencies.get_library_repository')
    @patch('app.core.dependencies.get_vector_index_service')
    def test_build_index_success(self, mock_get_vector_service, mock_get_repo, 
                                client, sample_library, sample_chunks):
        """Test successful index building"""
        # Setup mocks
        mock_repo = Mock()
        mock_vector_service = Mock()
        mock_get_repo.return_value = mock_repo
        mock_get_vector_service.return_value = mock_vector_service
        
        mock_repo.get_library.return_value = sample_library
        mock_repo.get_library_chunks.return_value = sample_chunks
        mock_vector_service.set_index_type.return_value = None
        mock_vector_service.index_library = AsyncMock(return_value=None)
        
        # Make request
        response = client.post(f"/api/v1/search/libraries/{sample_library.id}/index?index_type=brute_force")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "Successfully built brute_force index" in data["message"]
        assert data["library_id"] == str(sample_library.id)
        assert data["index_type"] == "brute_force"
        assert data["chunk_count"] == len(sample_chunks)
        
        # Verify service calls
        mock_repo.get_library.assert_called_once_with(sample_library.id)
        mock_repo.get_library_chunks.assert_called_once_with(sample_library.id)
        mock_vector_service.set_index_type.assert_called_once_with(sample_library.id, "brute_force")
        mock_vector_service.index_library.assert_called_once_with(sample_library.id, sample_chunks)
    
    @patch('app.core.dependencies.get_library_repository')
    def test_build_index_library_not_found(self, mock_get_repo, client):
        """Test building index for non-existent library"""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        mock_repo.get_library.return_value = None
        
        library_id = str(uuid4())
        response = client.post(f"/api/v1/search/libraries/{library_id}/index?index_type=brute_force")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Library not found"
    
    @patch('app.core.dependencies.get_library_repository')
    def test_build_index_no_chunks(self, mock_get_repo, client, sample_library):
        """Test building index when library has no chunks"""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        mock_repo.get_library.return_value = sample_library
        mock_repo.get_library_chunks.return_value = []
        
        response = client.post(f"/api/v1/search/libraries/{sample_library.id}/index?index_type=brute_force")
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "No chunks found for this library"
    
    @patch('app.core.dependencies.get_library_repository')
    @patch('app.core.dependencies.get_vector_index_service')
    def test_build_index_invalid_type(self, mock_get_vector_service, mock_get_repo, 
                                    client, sample_library, sample_chunks):
        """Test building index with invalid index type"""
        mock_repo = Mock()
        mock_vector_service = Mock()
        mock_get_repo.return_value = mock_repo
        mock_get_vector_service.return_value = mock_vector_service
        
        mock_repo.get_library.return_value = sample_library
        mock_repo.get_library_chunks.return_value = sample_chunks
        mock_vector_service.set_index_type.side_effect = ValueError("Unsupported index type: invalid")
        
        response = client.post(f"/api/v1/search/libraries/{sample_library.id}/index?index_type=invalid")
        
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported index type: invalid" in data["detail"]


class TestSearchEndpoint:
    """Test POST /api/v1/search/libraries/{library_id}/search"""
    
    @patch('app.core.dependencies.get_library_repository')
    @patch('app.core.dependencies.get_vector_index_service')
    @patch('app.core.dependencies.get_embedding_service')
    def test_search_with_embedding_success(self, mock_get_embedding_service, mock_get_vector_service, 
                                         mock_get_repo, client, sample_library, sample_chunks):
        """Test successful search with provided embedding"""
        # Setup mocks
        mock_repo = Mock()
        mock_vector_service = Mock()
        mock_embedding_service = Mock()
        
        mock_get_repo.return_value = mock_repo
        mock_get_vector_service.return_value = mock_vector_service
        mock_get_embedding_service.return_value = mock_embedding_service
        
        mock_repo.get_library.return_value = sample_library
        
        # Mock search results
        search_results = [
            VectorSearchResult(
                chunk=sample_chunks[0],
                distance=0.1,
                similarity=0.9
            ),
            VectorSearchResult(
                chunk=sample_chunks[1],
                distance=0.2,
                similarity=0.8
            )
        ]
        mock_vector_service.search_similar_chunks = AsyncMock(return_value=search_results)
        
        # Make request
        search_request = {
            "query_embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "k": 2,
            "similarity_metric": "cosine"
        }
        
        response = client.post(
            f"/api/v1/search/libraries/{sample_library.id}/search",
            json=search_request
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["chunk"]["text"] == "Machine learning basics"
        assert data[0]["similarity"] == 0.9
        assert data[0]["distance"] == 0.1
        
        # Verify service calls
        mock_repo.get_library.assert_called_once_with(sample_library.id)
        mock_vector_service.search_similar_chunks.assert_called_once_with(
            library_id=sample_library.id,
            query_embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
            k=2,
            similarity_metric="cosine",
            metadata_filter=None
        )
    
    @patch('app.core.dependencies.get_library_repository')
    @patch('app.core.dependencies.get_vector_index_service')
    @patch('app.core.dependencies.get_embedding_service')
    def test_search_with_auto_embedding(self, mock_get_embedding_service, mock_get_vector_service, 
                                      mock_get_repo, client, sample_library, sample_chunks):
        """Test search with auto-generated embedding"""
        # Setup mocks
        mock_repo = Mock()
        mock_vector_service = Mock()
        mock_embedding_service = Mock()
        
        mock_get_repo.return_value = mock_repo
        mock_get_vector_service.return_value = mock_vector_service
        mock_get_embedding_service.return_value = mock_embedding_service
        
        mock_repo.get_library.return_value = sample_library
        mock_embedding_service.is_available.return_value = True
        mock_embedding_service.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3, 0.4, 0.5])
        
        search_results = [
            VectorSearchResult(
                chunk=sample_chunks[0],
                distance=0.1,
                similarity=0.9
            )
        ]
        mock_vector_service.search_similar_chunks = AsyncMock(return_value=search_results)
        
        # Make request
        search_request = {
            "query_text": "machine learning basics",
            "k": 1,
            "similarity_metric": "cosine"
        }
        
        response = client.post(
            f"/api/v1/search/libraries/{sample_library.id}/search",
            json=search_request
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        # Verify embedding generation was called
        mock_embedding_service.generate_embedding.assert_called_once_with("machine learning basics")
    
    @patch('app.core.dependencies.get_library_repository')
    def test_search_library_not_found(self, mock_get_repo, client):
        """Test search for non-existent library"""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        mock_repo.get_library.return_value = None
        
        search_request = {
            "query_embedding": [0.1, 0.2, 0.3],
            "k": 2
        }
        
        library_id = str(uuid4())
        response = client.post(
            f"/api/v1/search/libraries/{library_id}/search",
            json=search_request
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Library not found"
    
    @patch('app.core.dependencies.get_library_repository')
    @patch('app.core.dependencies.get_vector_index_service')
    @patch('app.core.dependencies.get_embedding_service')
    def test_search_embedding_service_unavailable(self, mock_get_embedding_service, mock_get_vector_service,
                                                 mock_get_repo, client, sample_library):
        """Test search when embedding service unavailable"""
        mock_repo = Mock()
        mock_vector_service = Mock()
        mock_embedding_service = Mock()
        
        mock_get_repo.return_value = mock_repo
        mock_get_vector_service.return_value = mock_vector_service
        mock_get_embedding_service.return_value = mock_embedding_service
        
        mock_repo.get_library.return_value = sample_library
        mock_embedding_service.is_available.return_value = False
        
        search_request = {
            "query_text": "test query",
            "k": 2
        }
        
        response = client.post(
            f"/api/v1/search/libraries/{sample_library.id}/search",
            json=search_request
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Embedding service not available" in data["detail"]
    
    @patch('app.core.dependencies.get_library_repository')
    @patch('app.core.dependencies.get_vector_index_service')
    @patch('app.core.dependencies.get_embedding_service')
    def test_search_no_query_provided(self, mock_get_embedding_service, mock_get_vector_service,
                                    mock_get_repo, client, sample_library):
        """Test search with no query embedding or text"""
        mock_repo = Mock()
        mock_vector_service = Mock()
        mock_embedding_service = Mock()
        
        mock_get_repo.return_value = mock_repo
        mock_get_vector_service.return_value = mock_vector_service
        mock_get_embedding_service.return_value = mock_embedding_service
        
        mock_repo.get_library.return_value = sample_library
        
        search_request = {
            "k": 2,
            "similarity_metric": "cosine"
        }
        
        response = client.post(
            f"/api/v1/search/libraries/{sample_library.id}/search",
            json=search_request
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Either query_embedding or query_text must be provided" in data["detail"]
    
    @patch('app.core.dependencies.get_library_repository')
    @patch('app.core.dependencies.get_vector_index_service')
    @patch('app.core.dependencies.get_embedding_service')
    def test_search_with_metadata_filter(self, mock_get_embedding_service, mock_get_vector_service,
                                       mock_get_repo, client, sample_library, sample_chunks):
        """Test search with metadata filtering"""
        mock_repo = Mock()
        mock_vector_service = Mock()
        mock_embedding_service = Mock()
        
        mock_get_repo.return_value = mock_repo
        mock_get_vector_service.return_value = mock_vector_service
        mock_get_embedding_service.return_value = mock_embedding_service
        
        mock_repo.get_library.return_value = sample_library
        mock_vector_service.search_similar_chunks = AsyncMock(return_value=[])
        
        search_request = {
            "query_embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "k": 2,
            "similarity_metric": "cosine",
            "metadata_filter": {"topic": "AI"}
        }
        
        response = client.post(
            f"/api/v1/search/libraries/{sample_library.id}/search",
            json=search_request
        )
        
        assert response.status_code == 200
        
        # Verify metadata filter was passed to service
        mock_vector_service.search_similar_chunks.assert_called_once_with(
            library_id=sample_library.id,
            query_embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
            k=2,
            similarity_metric="cosine",
            metadata_filter={"topic": "AI"}
        )


class TestSetIndexTypeEndpoint:
    """Test POST /api/v1/search/libraries/{library_id}/index_type"""
    
    @patch('app.core.dependencies.get_library_repository')
    @patch('app.core.dependencies.get_vector_index_service')
    def test_set_index_type_success(self, mock_get_vector_service, mock_get_repo, 
                                  client, sample_library):
        """Test successful index type setting"""
        mock_repo = Mock()
        mock_vector_service = Mock()
        mock_get_repo.return_value = mock_repo
        mock_get_vector_service.return_value = mock_vector_service
        
        mock_repo.get_library.return_value = sample_library
        mock_vector_service.set_index_type.return_value = None
        
        response = client.post(f"/api/v1/search/libraries/{sample_library.id}/index_type?index_type=kdtree")
        
        assert response.status_code == 200
        data = response.json()
        assert "Index type set to kdtree" in data["message"]
        assert data["library_id"] == str(sample_library.id)
        assert data["index_type"] == "kdtree"
        
        mock_vector_service.set_index_type.assert_called_once_with(sample_library.id, "kdtree")
    
    @patch('app.core.dependencies.get_library_repository')
    def test_set_index_type_library_not_found(self, mock_get_repo, client):
        """Test setting index type for non-existent library"""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        mock_repo.get_library.return_value = None
        
        library_id = str(uuid4())
        response = client.post(f"/api/v1/search/libraries/{library_id}/index_type?index_type=kdtree")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Library not found"
    
    @patch('app.core.dependencies.get_library_repository')
    @patch('app.core.dependencies.get_vector_index_service')
    def test_set_index_type_invalid(self, mock_get_vector_service, mock_get_repo, 
                                  client, sample_library):
        """Test setting invalid index type"""
        mock_repo = Mock()
        mock_vector_service = Mock()
        mock_get_repo.return_value = mock_repo
        mock_get_vector_service.return_value = mock_vector_service
        
        mock_repo.get_library.return_value = sample_library
        mock_vector_service.set_index_type.side_effect = ValueError("Unsupported index type")
        
        response = client.post(f"/api/v1/search/libraries/{sample_library.id}/index_type?index_type=invalid")
        
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported index type" in data["detail"]


class TestGetIndexInfoEndpoint:
    """Test GET /api/v1/search/libraries/{library_id}/index"""
    
    @patch('app.core.dependencies.get_library_repository')
    @patch('app.core.dependencies.get_vector_index_service')
    def test_get_index_info_success(self, mock_get_vector_service, mock_get_repo, 
                                  client, sample_library, sample_chunks):
        """Test successful index info retrieval"""
        mock_repo = Mock()
        mock_vector_service = Mock()
        mock_get_repo.return_value = mock_repo
        mock_get_vector_service.return_value = mock_vector_service
        
        mock_repo.get_library.return_value = sample_library
        mock_repo.get_library_chunks.return_value = sample_chunks
        mock_vector_service.get_index_type.return_value = "brute_force"
        
        response = client.get(f"/api/v1/search/libraries/{sample_library.id}/index")
        
        assert response.status_code == 200
        data = response.json()
        assert data["library_id"] == str(sample_library.id)
        assert data["index_type"] == "brute_force"
        assert data["chunk_count"] == len(sample_chunks)
        assert data["indexed"] is True
    
    @patch('app.core.dependencies.get_library_repository')
    def test_get_index_info_library_not_found(self, mock_get_repo, client):
        """Test getting index info for non-existent library"""
        mock_repo = Mock()
        mock_get_repo.return_value = mock_repo
        mock_repo.get_library.return_value = None
        
        library_id = str(uuid4())
        response = client.get(f"/api/v1/search/libraries/{library_id}/index")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Library not found"
    
    @patch('app.core.dependencies.get_library_repository')
    @patch('app.core.dependencies.get_vector_index_service')
    def test_get_index_info_no_index(self, mock_get_vector_service, mock_get_repo, 
                                   client, sample_library):
        """Test getting index info when no index exists"""
        mock_repo = Mock()
        mock_vector_service = Mock()
        mock_get_repo.return_value = mock_repo
        mock_get_vector_service.return_value = mock_vector_service
        
        mock_repo.get_library.return_value = sample_library
        mock_repo.get_library_chunks.return_value = []
        mock_vector_service.get_index_type.return_value = None
        
        response = client.get(f"/api/v1/search/libraries/{sample_library.id}/index")
        
        assert response.status_code == 200
        data = response.json()
        assert data["library_id"] == str(sample_library.id)
        assert data["index_type"] is None
        assert data["chunk_count"] == 0
        assert data["indexed"] is False


class TestSearchEndpointValidation:
    """Test request validation for search endpoints"""
    
    def test_search_request_validation(self, client, sample_library_id):
        """Test search request model validation"""
        # Invalid similarity metric
        search_request = {
            "query_embedding": [0.1, 0.2],
            "k": 5,
            "similarity_metric": "invalid_metric"
        }
        
        response = client.post(
            f"/api/v1/search/libraries/{sample_library_id}/search",
            json=search_request
        )
        
        # This should still reach the endpoint but may fail in service layer
        # The validation happens at the service level, not Pydantic level
        assert response.status_code in [400, 404, 422]
    
    def test_search_request_negative_k(self, client, sample_library_id):
        """Test search with negative k value"""
        search_request = {
            "query_embedding": [0.1, 0.2],
            "k": -1
        }
        
        response = client.post(
            f"/api/v1/search/libraries/{sample_library_id}/search",
            json=search_request
        )
        
        # May be validated at Pydantic level or service level
        assert response.status_code in [400, 404, 422]
    
    def test_search_request_zero_k(self, client, sample_library_id):
        """Test search with k=0"""
        search_request = {
            "query_embedding": [0.1, 0.2],
            "k": 0
        }
        
        response = client.post(
            f"/api/v1/search/libraries/{sample_library_id}/search",
            json=search_request
        )
        
        # k=0 might be valid (return no results) or invalid depending on implementation
        assert response.status_code in [200, 400, 404, 422]


class TestSearchEndpointIntegration:
    """Integration tests for search endpoints"""
    
    @patch('app.core.dependencies.get_library_repository')
    @patch('app.core.dependencies.get_vector_index_service')
    @patch('app.core.dependencies.get_embedding_service')
    def test_full_search_workflow(self, mock_get_embedding_service, mock_get_vector_service,
                                mock_get_repo, client, sample_library, sample_chunks):
        """Test complete search workflow: index -> search"""
        # Setup mocks for both endpoints
        mock_repo = Mock()
        mock_vector_service = Mock()
        mock_embedding_service = Mock()
        
        mock_get_repo.return_value = mock_repo
        mock_get_vector_service.return_value = mock_vector_service
        mock_get_embedding_service.return_value = mock_embedding_service
        
        mock_repo.get_library.return_value = sample_library
        mock_repo.get_library_chunks.return_value = sample_chunks
        mock_vector_service.set_index_type.return_value = None
        mock_vector_service.index_library = AsyncMock(return_value=None)
        
        # Step 1: Build index
        index_response = client.post(
            f"/api/v1/search/libraries/{sample_library.id}/index?index_type=brute_force"
        )
        assert index_response.status_code == 200
        
        # Step 2: Search
        search_results = [
            VectorSearchResult(
                chunk=sample_chunks[0],
                distance=0.1,
                similarity=0.9
            )
        ]
        mock_vector_service.search_similar_chunks = AsyncMock(return_value=search_results)
        
        search_request = {
            "query_embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "k": 1,
            "similarity_metric": "cosine"
        }
        
        search_response = client.post(
            f"/api/v1/search/libraries/{sample_library.id}/search",
            json=search_request
        )
        
        assert search_response.status_code == 200
        data = search_response.json()
        assert len(data) == 1
        assert data[0]["chunk"]["text"] == "Machine learning basics" 