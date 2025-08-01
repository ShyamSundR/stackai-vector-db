"""
StackAI Vector Database Python Client

Main client class for interacting with the StackAI Vector Database API.
"""

import json
import requests
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin
import time

from .models import Library, Document, Chunk, SearchResult, IndexInfo, HealthStatus
from .exceptions import APIException, ConnectionException, TimeoutException, ValidationException


class StackAIClient:
    """
    Python client for StackAI Vector Database API
    
    Provides methods for managing libraries, documents, chunks, and performing
    vector similarity search with advanced metadata filtering.
    
    Args:
        base_url (str): Base URL of the StackAI API (e.g., "http://localhost:8000")
        api_version (str): API version to use (default: "v1")
        timeout (int): Request timeout in seconds (default: 30)
        verify_ssl (bool): Whether to verify SSL certificates (default: True)
        
    Example:
        client = StackAIClient("http://localhost:8000")
        
        # Create a library
        library = client.create_library("My Library", "Description")
        
        # Search with auto-embedding
        results = client.search(
            library_id=library.id,
            query_text="machine learning",
            auto_embed=True,
            k=5
        )
    """
    
    def __init__(self, 
                 base_url: str,
                 api_version: str = "v1", 
                 timeout: int = 30,
                 verify_ssl: bool = True):
        self.base_url = base_url.rstrip('/')
        self.api_version = api_version
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # Build API base URL
        self.api_base = f"{self.base_url}/api/{api_version}"
        
        # Session for connection pooling
        self.session = requests.Session()
        
    def _make_request(self, 
                     method: str, 
                     endpoint: str, 
                     data: dict = None, 
                     params: dict = None,
                     json_data: dict = None) -> requests.Response:
        """Make HTTP request to the API"""
        url = urljoin(self.api_base + "/", endpoint.lstrip("/"))
        
        try:
            if json_data:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    timeout=self.timeout,
                    verify=self.verify_ssl
                )
            else:
                response = self.session.request(
                    method=method,
                    url=url,
                    data=data,
                    params=params,
                    timeout=self.timeout,
                    verify=self.verify_ssl
                )
                
            # Raise exception for HTTP errors
            if not response.ok:
                try:
                    error_data = response.json()
                    message = error_data.get('detail', response.text)
                    details = error_data if isinstance(error_data, dict) else {}
                except:
                    message = response.text
                    details = {}
                    
                raise APIException(response.status_code, message, details)
                
            return response
            
        except requests.exceptions.Timeout:
            raise TimeoutException(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise ConnectionException(f"Failed to connect to {url}")
        except requests.exceptions.RequestException as e:
            raise ConnectionException(f"Request failed: {str(e)}")
    
    def health_check(self) -> HealthStatus:
        """Check API health status"""
        response = self._make_request("GET", f"{self.base_url}/health")
        return HealthStatus.from_dict(response.json())
    
    def get_embedding_status(self) -> dict:
        """Get embedding service status"""
        response = self._make_request("GET", "search/embedding/status")
        return response.json()
    
    # Library operations
    def create_library(self, name: str, description: str = "", metadata: Dict[str, Any] = None) -> Library:
        """Create a new library"""
        if not name.strip():
            raise ValidationException("Library name cannot be empty")
            
        # Add description to metadata if provided
        lib_metadata = metadata or {}
        if description:
            lib_metadata["description"] = description
            
        data = {"name": name, "metadata": lib_metadata}
        response = self._make_request("POST", "libraries/", json_data=data)
        return Library.from_dict(response.json())
    
    def get_library(self, library_id: str) -> Library:
        """Get library by ID"""
        response = self._make_request("GET", f"libraries/{library_id}")
        return Library.from_dict(response.json())
    
    def list_libraries(self) -> List[Library]:
        """List all libraries"""
        response = self._make_request("GET", "libraries/")
        return [Library.from_dict(lib) for lib in response.json()]
    
    def update_library(self, library_id: str, name: str = None, description: str = None, metadata: Dict[str, Any] = None) -> Library:
        """Update library"""
        data = {}
        if name is not None:
            data["name"] = name
        if metadata is not None or description is not None:
            # Get current library to preserve existing metadata
            current_lib = self.get_library(library_id)
            update_metadata = current_lib.metadata.copy() if hasattr(current_lib, 'metadata') else {}
            
            if metadata is not None:
                update_metadata.update(metadata)
            if description is not None:
                update_metadata["description"] = description
                
            data["metadata"] = update_metadata
            
        if not data:
            raise ValidationException("At least one field must be provided for update")
            
        response = self._make_request("PUT", f"libraries/{library_id}", json_data=data)
        return Library.from_dict(response.json())
    
    def delete_library(self, library_id: str) -> bool:
        """Delete library"""
        self._make_request("DELETE", f"libraries/{library_id}")
        return True
    
    # Document operations
    def create_document(self, title: str, library_id: str, metadata: Dict[str, Any] = None) -> Document:
        """Create a new document"""
        if not title.strip():
            raise ValidationException("Document title cannot be empty")
            
        data = {
            "title": title,
            "library_id": library_id,
            "metadata": metadata or {}
        }
        response = self._make_request("POST", "documents/", json_data=data)
        return Document.from_dict(response.json())
    
    def get_document(self, document_id: str) -> Document:
        """Get document by ID"""
        response = self._make_request("GET", f"documents/{document_id}")
        return Document.from_dict(response.json())
    
    def list_documents(self, library_id: str = None) -> List[Document]:
        """List documents, optionally filtered by library"""
        params = {"library_id": library_id} if library_id else None
        response = self._make_request("GET", "documents/", params=params)
        return [Document.from_dict(doc) for doc in response.json()]
    
    def update_document(self, document_id: str, title: str = None, metadata: Dict[str, Any] = None) -> Document:
        """Update document"""
        data = {}
        if title is not None:
            data["title"] = title
        if metadata is not None:
            data["metadata"] = metadata
            
        if not data:
            raise ValidationException("At least one field must be provided for update")
            
        response = self._make_request("PUT", f"documents/{document_id}", json_data=data)
        return Document.from_dict(response.json())
    
    def delete_document(self, document_id: str) -> bool:
        """Delete document"""
        self._make_request("DELETE", f"documents/{document_id}")
        return True
    
    # Chunk operations
    def create_chunk(self, 
                    text: str,
                    document_id: str,
                    embedding: List[float] = None,
                    metadata: Dict[str, Any] = None,
                    auto_embed: bool = False) -> Chunk:
        """Create a new chunk"""
        if not text.strip():
            raise ValidationException("Chunk text cannot be empty")
            
        data = {
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {},
            "auto_embed": auto_embed
        }
        
        params = {"document_id": document_id}
        response = self._make_request("POST", "chunks/", json_data=data, params=params)
        return Chunk.from_dict(response.json())
    
    def get_chunk(self, chunk_id: str) -> Chunk:
        """Get chunk by ID"""
        response = self._make_request("GET", f"chunks/{chunk_id}")
        return Chunk.from_dict(response.json())
    
    def list_chunks_by_document(self, document_id: str) -> List[Chunk]:
        """List chunks in a document"""
        response = self._make_request("GET", f"chunks/document/{document_id}")
        return [Chunk.from_dict(chunk) for chunk in response.json()]
    
    def list_chunks_by_library(self, library_id: str) -> List[Chunk]:
        """List chunks in a library"""
        response = self._make_request("GET", f"chunks/library/{library_id}")
        return [Chunk.from_dict(chunk) for chunk in response.json()]
    
    def update_chunk(self, 
                    chunk_id: str,
                    text: str = None,
                    embedding: List[float] = None,
                    metadata: Dict[str, Any] = None,
                    auto_embed: bool = False) -> Chunk:
        """Update chunk"""
        data = {}
        if text is not None:
            data["text"] = text
        if embedding is not None:
            data["embedding"] = embedding
        if metadata is not None:
            data["metadata"] = metadata
        data["auto_embed"] = auto_embed
            
        if not any(key in data for key in ["text", "embedding", "metadata"]):
            raise ValidationException("At least one field must be provided for update")
            
        response = self._make_request("PUT", f"chunks/{chunk_id}", json_data=data)
        return Chunk.from_dict(response.json())
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete chunk"""
        self._make_request("DELETE", f"chunks/{chunk_id}")
        return True
    
    # Index operations
    def build_index(self, library_id: str, index_type: str = "brute_force") -> IndexInfo:
        """Build vector index for a library"""
        if index_type not in ["brute_force", "kdtree"]:
            raise ValidationException("index_type must be 'brute_force' or 'kdtree'")
            
        params = {"index_type": index_type}
        response = self._make_request("POST", f"search/libraries/{library_id}/index", params=params)
        return IndexInfo.from_dict(response.json())
    
    def get_index_type(self, library_id: str) -> str:
        """Get current index type for a library"""
        response = self._make_request("GET", f"search/libraries/{library_id}/index_type")
        return response.json()["index_type"]
    
    def set_index_type(self, library_id: str, index_type: str) -> IndexInfo:
        """Set index type for a library"""
        if index_type not in ["brute_force", "kdtree"]:
            raise ValidationException("index_type must be 'brute_force' or 'kdtree'")
            
        params = {"index_type": index_type}
        response = self._make_request("POST", f"search/libraries/{library_id}/index_type", params=params)
        return IndexInfo.from_dict(response.json())
    
    # Search operations
    def search(self,
              library_id: str,
              query_embedding: List[float] = None,
              query_text: str = None,
              auto_embed: bool = False,
              k: int = 5,
              similarity_metric: str = "cosine",
              metadata_filter: Dict[str, Any] = None) -> List[SearchResult]:
        """
        Perform vector similarity search
        
        Args:
            library_id: ID of the library to search
            query_embedding: Vector embedding for search (optional if using auto_embed)
            query_text: Text query for auto-embedding (requires auto_embed=True)
            auto_embed: Whether to generate embedding from query_text using Cohere
            k: Number of results to return (1-100)
            similarity_metric: Similarity metric ("cosine", "euclidean", "dot_product")
            metadata_filter: Advanced metadata filtering conditions
            
        Returns:
            List of SearchResult objects
            
        Example metadata filters:
            {"category": "healthcare"}  # Simple equality
            {"rating": {"$gt": 4.0}}    # Numeric comparison
            {"tags": {"$in": ["ML", "AI"]}}  # Array membership
            {"author.name": {"$contains": "Smith"}}  # String contains with nested field
            {"date": {"$date_after": "2024-01-01"}}  # Date comparison
        """
        if k < 1 or k > 100:
            raise ValidationException("k must be between 1 and 100")
            
        if similarity_metric not in ["cosine", "euclidean", "dot_product"]:
            raise ValidationException("similarity_metric must be 'cosine', 'euclidean', or 'dot_product'")
            
        if not query_embedding and not (query_text and auto_embed):
            raise ValidationException("Either query_embedding or (query_text + auto_embed=True) must be provided")
        
        data = {
            "query_embedding": query_embedding,
            "query_text": query_text,
            "auto_embed": auto_embed,
            "k": k,
            "similarity_metric": similarity_metric,
            "metadata_filter": metadata_filter
        }
        
        response = self._make_request("POST", f"search/libraries/{library_id}/search", json_data=data)
        results_data = response.json()
        
        return [SearchResult.from_dict(result) for result in results_data["results"]]
    
    # Convenience methods
    def create_library_with_documents(self, 
                                    library_name: str,
                                    documents: List[Dict[str, Any]],
                                    library_description: str = "",
                                    auto_embed: bool = False,
                                    index_type: str = "brute_force") -> Library:
        """
        Create a library and populate it with documents and chunks in one operation
        
        Args:
            library_name: Name of the library
            documents: List of document dictionaries with structure:
                      {"title": str, "chunks": [{"text": str, "metadata": dict}]}
            library_description: Description of the library
            auto_embed: Whether to auto-generate embeddings for chunks
            index_type: Type of index to build
            
        Returns:
            Created Library object
        """
        # Create library
        library = self.create_library(library_name, library_description)
        
        # Add documents and chunks
        for doc_data in documents:
            document = self.create_document(
                title=doc_data["title"],
                library_id=library.id,
                metadata=doc_data.get("metadata", {})
            )
            
            # Add chunks
            for chunk_data in doc_data.get("chunks", []):
                self.create_chunk(
                    text=chunk_data["text"],
                    document_id=document.id,
                    embedding=chunk_data.get("embedding", [0.1, 0.2, 0.3, 0.4, 0.5] if not auto_embed else None),
                    metadata=chunk_data.get("metadata", {}),
                    auto_embed=auto_embed
                )
        
        # Build index
        self.build_index(library.id, index_type)
        
        return library
    
    def bulk_search(self,
                   library_id: str,
                   queries: List[Dict[str, Any]],
                   default_k: int = 5) -> List[List[SearchResult]]:
        """
        Perform multiple searches in batch
        
        Args:
            library_id: ID of the library to search
            queries: List of query dictionaries with search parameters
            default_k: Default number of results if not specified in query
            
        Returns:
            List of result lists, one for each query
        """
        results = []
        for query in queries:
            query_params = {
                "library_id": library_id,
                "k": query.get("k", default_k),
                **query
            }
            results.append(self.search(**query_params))
        
        return results
    
    def wait_for_health(self, max_wait_time: int = 60) -> bool:
        """
        Wait for API to become healthy
        
        Args:
            max_wait_time: Maximum time to wait in seconds
            
        Returns:
            True if API becomes healthy, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            try:
                health = self.health_check()
                if health.status == "healthy":
                    return True
            except:
                pass
            time.sleep(1)
        
        return False
    
    def close(self):
        """Close the HTTP session"""
        if self.session:
            self.session.close() 