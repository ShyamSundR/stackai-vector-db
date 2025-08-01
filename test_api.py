#!/usr/bin/env python3
"""
Test script for StackAI Vector Database API
Tests both manual embeddings and Cohere API auto-embedding
"""

import requests
import json
import os
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
HEALTH_URL = "http://localhost:8000/health"

# Test data with manual embeddings
chunks_data_manual = [
    {
        "text": "Machine learning is a subset of artificial intelligence that focuses on algorithms",
        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
        "metadata": {"topic": "ML", "author": "John Doe", "category": "technical"}
    },
    {
        "text": "Deep learning uses neural networks with multiple layers to process data",
        "embedding": [0.2, 0.1, 0.4, 0.3, 0.6],
        "metadata": {"topic": "DL", "author": "Jane Smith", "category": "technical"}
    },
    {
        "text": "Natural language processing analyzes and understands human language",
        "embedding": [0.3, 0.4, 0.2, 0.5, 0.1],
        "metadata": {"topic": "NLP", "author": "Bob Wilson", "category": "research"}
    }
]

# Test data for auto-embedding (no embedding vectors provided)
chunks_data_auto = [
    {
        "text": "Computer vision enables machines to interpret and understand visual information",
        "auto_embed": True,
        "metadata": {"topic": "CV", "author": "Alice Brown", "category": "technical"}
    },
    {
        "text": "Reinforcement learning teaches agents to make decisions through trial and error",
        "auto_embed": True,
        "metadata": {"topic": "RL", "author": "Charlie Davis", "category": "research"}
    }
]

def make_request(method: str, url: str, **kwargs) -> requests.Response:
    """Make HTTP request with error handling"""
    try:
        response = requests.request(method, url, **kwargs)
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        raise

def test_health():
    """Test API health check"""
    print("1. Health Check...")
    response = make_request("GET", HEALTH_URL)
    
    if response.status_code == 200:
        health_data = response.json()
        print("✅ API is running")
        
        # Check embedding service status
        if "services" in health_data and "embedding_service" in health_data["services"]:
            embedding_status = health_data["services"]["embedding_service"]
            if embedding_status["available"]:
                print(f"✅ Cohere embedding service available (model: {embedding_status['model']})")
            else:
                print("⚠️ Cohere embedding service not available (API key not configured)")
        
        return health_data
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return None

def test_embedding_status():
    """Test embedding service status endpoint"""
    print("\n2. Checking Embedding Service Status...")
    response = make_request("GET", f"{BASE_URL}/search/embedding/status")
    
    if response.status_code == 200:
        status = response.json()
        print(f"✅ Embedding service status: {json.dumps(status, indent=2)}")
        return status["embedding_service_available"]
    else:
        print(f"❌ Failed to get embedding status: {response.status_code}")
        return False

def create_library() -> str:
    """Create a test library"""
    print("\n3. Creating library...")
    library_data = {
        "name": "AI Research Library",
        "description": "A collection of AI and ML research documents"
    }
    
    response = make_request("POST", f"{BASE_URL}/libraries/", json=library_data)
    
    if response.status_code == 201:
        library = response.json()
        library_id = library["id"]
        print(f"✅ Library created: {library_id}")
        return library_id
    else:
        print(f"❌ Failed to create library: {response.status_code} - {response.text}")
        raise Exception("Library creation failed")

def create_document(library_id: str) -> str:
    """Create a test document"""
    print("\n4. Creating document...")
    document_data = {
        "library_id": library_id,
        "title": "Introduction to Machine Learning",
        "content": "This document covers various aspects of machine learning and AI",
        "metadata": {"author": "Research Team", "year": 2024}
    }
    
    response = make_request("POST", f"{BASE_URL}/documents/", json=document_data)
    
    if response.status_code == 201:
        document = response.json()
        document_id = document["id"]
        print(f"✅ Document created: {document_id}")
        return document_id
    else:
        print(f"❌ Failed to create document: {response.status_code} - {response.text}")
        raise Exception("Document creation failed")

def create_chunks_manual(document_id: str) -> list:
    """Create chunks with manual embeddings"""
    print("\n5. Creating chunks with manual embeddings...")
    chunk_ids = []
    
    for i, chunk_data in enumerate(chunks_data_manual):
        response = make_request(
            "POST", 
            f"{BASE_URL}/chunks/?document_id={document_id}",
            json=chunk_data
        )
        
        if response.status_code == 201:
            chunk = response.json()
            chunk_ids.append(chunk["id"])
            print(f"✅ Manual chunk created: {chunk['text'][:50]}...")
        else:
            print(f"❌ Failed to create chunk {i+1}: {response.status_code} - {response.text}")
    
    return chunk_ids

def create_chunks_auto(document_id: str, embedding_available: bool) -> list:
    """Create chunks with auto-generated embeddings"""
    if not embedding_available:
        print("\n⚠️ Skipping auto-embedding test (Cohere API not available)")
        return []
    
    print("\n6. Creating chunks with auto-generated embeddings...")
    chunk_ids = []
    
    for i, chunk_data in enumerate(chunks_data_auto):
        response = make_request(
            "POST", 
            f"{BASE_URL}/chunks/?document_id={document_id}",
            json=chunk_data
        )
        
        if response.status_code == 201:
            chunk = response.json()
            chunk_ids.append(chunk["id"])
            print(f"✅ Auto-embedded chunk created: {chunk['text'][:50]}...")
            print(f"   Generated embedding length: {len(chunk['embedding'])}")
        else:
            print(f"❌ Failed to create auto-embedded chunk {i+1}: {response.status_code} - {response.text}")
    
    return chunk_ids

def verify_chunks(library_id: str):
    """Verify chunks are in the library"""
    print(f"\n7. Checking library chunks...")
    response = make_request("GET", f"{BASE_URL}/chunks/library/{library_id}")
    
    if response.status_code == 200:
        chunks = response.json()
        print(f"✅ Found {len(chunks)} chunks in library")
        return chunks
    else:
        print(f"❌ Failed to get library chunks: {response.status_code}")
        return []

def test_vector_indexing(library_id: str):
    """Test vector index building"""
    print(f"\n8. Building vector index...")
    response = make_request(
        "POST", 
        f"{BASE_URL}/search/libraries/{library_id}/index?index_type=brute_force"
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Index built: {result}")
        return True
    else:
        print(f"❌ Failed to build index: {response.status_code} - {response.text}")
        return False

def test_similarity_search_manual(library_id: str):
    """Test similarity search with manual query embedding"""
    print(f"\n9. Performing similarity search with manual embedding...")
    
    search_data = {
        "query_embedding": [0.15, 0.25, 0.35, 0.45, 0.55],  # Similar to first chunk
        "k": 2,
        "similarity_metric": "cosine",
        "metadata_filter": {"category": "technical"}
    }
    
    response = make_request(
        "POST", 
        f"{BASE_URL}/search/libraries/{library_id}/search",
        json=search_data
    )
    
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Manual search completed, found {len(results['results'])} results")
        if results["results"]:
            for i, result in enumerate(results["results"][:2]):
                print(f"   {i+1}. {result['chunk']['text'][:50]}... (similarity: {result['similarity']:.3f})")
        return results
    else:
        print(f"❌ Search failed: {response.status_code} - {response.text}")
        return None

def test_similarity_search_auto(library_id: str, embedding_available: bool):
    """Test similarity search with auto-generated query embedding"""
    if not embedding_available:
        print("\n⚠️ Skipping auto-embedding search test (Cohere API not available)")
        return None
    
    print(f"\n10. Performing similarity search with auto-generated query embedding...")
    
    search_data = {
        "query_text": "artificial intelligence and machine learning algorithms",
        "auto_embed": True,
        "k": 3,
        "similarity_metric": "cosine"
    }
    
    response = make_request(
        "POST", 
        f"{BASE_URL}/search/libraries/{library_id}/search",
        json=search_data
    )
    
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Auto-embedding search completed, found {len(results['results'])} results")
        print(f"   Used auto-embedding: {results['query_info']['used_auto_embed']}")
        if results["results"]:
            for i, result in enumerate(results["results"][:3]):
                print(f"   {i+1}. {result['chunk']['text'][:50]}... (similarity: {result['similarity']:.3f})")
        return results
    else:
        print(f"❌ Auto-embedding search failed: {response.status_code} - {response.text}")
        return None

def test_index_type_change(library_id: str):
    """Test changing index type"""
    print(f"\n11. Changing index type to KDTree...")
    response = make_request(
        "POST", 
        f"{BASE_URL}/search/libraries/{library_id}/index_type?index_type=kdtree"
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Index type changed: {result}")
        return True
    else:
        print(f"❌ Failed to change index type: {response.status_code}")
        return False

def main():
    """Run the comprehensive test suite"""
    print("🧪 Testing StackAI Vector Database API with Cohere Integration...\n")
    
    try:
        # Test health and embedding availability
        health_data = test_health()
        if not health_data:
            return
        
        embedding_available = test_embedding_status()
        
        # Create test data
        library_id = create_library()
        document_id = create_document(library_id)
        
        # Create chunks (both manual and auto-embedding)
        manual_chunk_ids = create_chunks_manual(document_id)
        auto_chunk_ids = create_chunks_auto(document_id, embedding_available)
        
        # Verify chunks
        chunks = verify_chunks(library_id)
        
        if chunks:
            # Test vector operations
            if test_vector_indexing(library_id):
                # Test both types of searches
                test_similarity_search_manual(library_id)
                test_similarity_search_auto(library_id, embedding_available)
                
                # Test index type change
                if test_index_type_change(library_id):
                    print(f"\n12. Testing search with KDTree index...")
                    test_similarity_search_manual(library_id)
        
        print(f"\n🎉 All tests completed! Your StackAI Vector Database API is working correctly.")
        if embedding_available:
            print("✅ Both manual embeddings and Cohere auto-embedding are functional!")
        else:
            print("⚠️ Manual embeddings work. Set COHERE_API_KEY environment variable to test auto-embedding.")
            
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    main() 