"""
StackAI Vector Database Python SDK

A comprehensive Python client for the StackAI Vector Database API.
Provides easy-to-use methods for managing libraries, documents, chunks,
and performing vector similarity search with advanced metadata filtering.

Example:
    from stackai_sdk import StackAIClient
    
    # Initialize client
    client = StackAIClient(base_url="http://localhost:8000")
    
    # Create library and add documents
    library = client.create_library("My Library", "Description")
    document = client.create_document("My Document", library.id)
    
    # Add chunks with auto-embedding
    chunk = client.create_chunk(
        text="Machine learning is transforming healthcare",
        document_id=document.id,
        auto_embed=True,
        metadata={"category": "healthcare", "importance": "high"}
    )
    
    # Build index and search
    client.build_index(library.id, index_type="kdtree")
    results = client.search(
        library_id=library.id,
        query_text="AI in medical field",
        auto_embed=True,
        k=5,
        metadata_filter={"category": "healthcare"}
    )
"""

from .client import StackAIClient
from .models import Library, Document, Chunk, SearchResult
from .exceptions import StackAIException, APIException, ValidationException

__version__ = "1.0.0"
__author__ = "StackAI Team"
__email__ = "contact@stackai.com"

__all__ = [
    "StackAIClient",
    "Library", 
    "Document",
    "Chunk",
    "SearchResult",
    "StackAIException",
    "APIException", 
    "ValidationException"
] 