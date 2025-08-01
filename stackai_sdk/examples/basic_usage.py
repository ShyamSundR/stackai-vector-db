#!/usr/bin/env python3
"""
StackAI SDK Basic Usage Examples

This script demonstrates the basic functionality of the StackAI Python SDK.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from stackai_sdk import StackAIClient
from stackai_sdk.exceptions import APIException, ValidationException


def basic_example():
    """Basic usage example"""
    print("🚀 StackAI SDK Basic Usage Example\n")
    
    # Initialize client
    client = StackAIClient(base_url="http://localhost:8000")
    
    try:
        # Check API health
        print("1. Health Check")
        health = client.health_check()
        print(f"   Status: {health.status}")
        print(f"   App: {health.app} v{health.version}")
        
        # Check embedding service
        embed_status = client.get_embedding_status()
        print(f"   Embedding Service: {'Available' if embed_status['embedding_service_available'] else 'Not Available'}")
        print()
        
        # Create a library
        print("2. Creating Library")
        library = client.create_library(
            name="AI Research Papers",
            description="Collection of AI and ML research papers"
        )
        print(f"   Library created: {library.name} (ID: {library.id})")
        print()
        
        # Create documents
        print("3. Creating Documents")
        doc1 = client.create_document(
            title="Machine Learning Fundamentals",
            library_id=library.id,
            metadata={"category": "ML", "year": 2024}
        )
        
        doc2 = client.create_document(
            title="Deep Learning Applications",
            library_id=library.id,
            metadata={"category": "DL", "year": 2024}
        )
        
        print(f"   Document 1: {doc1.title} (ID: {doc1.id})")
        print(f"   Document 2: {doc2.title} (ID: {doc2.id})")
        print()
        
        # Create chunks with manual embeddings
        print("4. Creating Chunks (Manual Embeddings)")
        chunk1 = client.create_chunk(
            text="Machine learning is a subset of artificial intelligence that focuses on algorithms.",
            document_id=doc1.id,
            embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
            metadata={"section": "introduction", "importance": "high"}
        )
        
        chunk2 = client.create_chunk(
            text="Supervised learning uses labeled data to train predictive models.",
            document_id=doc1.id,
            embedding=[0.2, 0.3, 0.4, 0.5, 0.6],
            metadata={"section": "supervised", "importance": "medium"}
        )
        
        print(f"   Chunk 1 created: {chunk1.id}")
        print(f"   Chunk 2 created: {chunk2.id}")
        print()
        
        # Create chunks with auto-embedding (if Cohere is available)
        print("5. Creating Chunks (Auto-Embedding)")
        try:
            chunk3 = client.create_chunk(
                text="Deep neural networks can learn complex patterns from large datasets.",
                document_id=doc2.id,
                auto_embed=True,
                metadata={"section": "deep_learning", "importance": "high"}
            )
            print(f"   Auto-embedded chunk created: {chunk3.id}")
            print(f"   Embedding length: {len(chunk3.embedding) if chunk3.embedding else 'None'}")
        except APIException as e:
            print(f"   Auto-embedding failed: {e.message}")
            # Fallback to manual embedding
            chunk3 = client.create_chunk(
                text="Deep neural networks can learn complex patterns from large datasets.",
                document_id=doc2.id,
                embedding=[0.3, 0.4, 0.5, 0.6, 0.7],
                metadata={"section": "deep_learning", "importance": "high"}
            )
            print(f"   Fallback chunk created: {chunk3.id}")
        print()
        
        # Build index
        print("6. Building Vector Index")
        index_info = client.build_index(library.id, index_type="brute_force")
        print(f"   Index built: {index_info.status} ({index_info.index_type})")
        print(f"   Message: {index_info.message}")
        print()
        
        # Perform searches
        print("7. Vector Similarity Search")
        
        # Manual embedding search
        results = client.search(
            library_id=library.id,
            query_embedding=[0.15, 0.25, 0.35, 0.45, 0.55],
            k=3,
            similarity_metric="cosine"
        )
        
        print(f"   Manual embedding search found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"      {i}. {result.chunk.text[:50]}... (similarity: {result.similarity:.3f})")
        print()
        
        # Auto-embedding search (if available)
        print("8. Auto-Embedding Search")
        try:
            results = client.search(
                library_id=library.id,
                query_text="What is machine learning?",
                auto_embed=True,
                k=2
            )
            print(f"   Auto-embedding search found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"      {i}. {result.chunk.text[:50]}... (similarity: {result.similarity:.3f})")
        except APIException as e:
            print(f"   Auto-embedding search failed: {e.message}")
        print()
        
        # Metadata filtering
        print("9. Search with Metadata Filter")
        results = client.search(
            library_id=library.id,
            query_embedding=[0.15, 0.25, 0.35, 0.45, 0.55],
            k=5,
            metadata_filter={"importance": "high"}
        )
        
        print(f"   High importance chunks found: {len(results)}")
        for i, result in enumerate(results, 1):
            print(f"      {i}. {result.chunk.metadata.get('section', 'N/A')} - {result.chunk.text[:40]}...")
        print()
        
        # List operations
        print("10. Listing Resources")
        
        libraries = client.list_libraries()
        print(f"   Total libraries: {len(libraries)}")
        
        documents = client.list_documents(library.id)
        print(f"   Documents in library: {len(documents)}")
        
        chunks = client.list_chunks_by_library(library.id)
        print(f"   Chunks in library: {len(chunks)}")
        
        print("\n✅ Basic example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        # Clean up
        client.close()


def advanced_metadata_filtering_example():
    """Advanced metadata filtering example"""
    print("\n🔍 Advanced Metadata Filtering Example\n")
    
    client = StackAIClient(base_url="http://localhost:8000")
    
    try:
        # Wait for API to be ready
        if not client.wait_for_health(30):
            print("❌ API not available")
            return
        
        # Create library with rich metadata
        library = client.create_library(
            name="Research Database",
            description="Advanced filtering demonstration"
        )
        
        document = client.create_document(
            title="Advanced AI Research",
            library_id=library.id
        )
        
        # Create chunks with rich metadata
        chunks_data = [
            {
                "text": "Transformer architectures revolutionized natural language processing.",
                "metadata": {
                    "category": "NLP",
                    "author": {"name": "Dr. Smith", "institution": "MIT"},
                    "rating": 4.8,
                    "citations": 1250,
                    "published_date": "2024-01-15",
                    "tags": ["transformers", "NLP", "architecture"],
                    "is_seminal": True
                }
            },
            {
                "text": "Computer vision models achieve human-level performance on image recognition.",
                "metadata": {
                    "category": "CV",
                    "author": {"name": "Prof. Johnson", "institution": "Stanford"},
                    "rating": 4.2,
                    "citations": 890,
                    "published_date": "2023-11-20",
                    "tags": ["computer vision", "image recognition"],
                    "is_seminal": False
                }
            },
            {
                "text": "Reinforcement learning enables autonomous decision-making systems.",
                "metadata": {
                    "category": "RL",
                    "author": {"name": "Dr. Smith", "institution": "MIT"},
                    "rating": 4.5,
                    "citations": 680,
                    "published_date": "2024-02-10",
                    "tags": ["reinforcement learning", "autonomous systems"],
                    "is_seminal": True
                }
            }
        ]
        
        # Create chunks
        for chunk_data in chunks_data:
            client.create_chunk(
                text=chunk_data["text"],
                document_id=document.id,
                embedding=[0.1, 0.2, 0.3, 0.4, 0.5],  # Dummy embedding
                metadata=chunk_data["metadata"]
            )
        
        # Build index
        client.build_index(library.id)
        
        # Test advanced filters
        filter_examples = [
            {
                "name": "High Rating Papers",
                "filter": {"rating": {"$gte": 4.5}},
                "description": "Papers with rating >= 4.5"
            },
            {
                "name": "MIT Authors",
                "filter": {"author.institution": "MIT"},
                "description": "Papers from MIT authors (nested field access)"
            },
            {
                "name": "Recent Seminal Papers",
                "filter": {
                    "is_seminal": True,
                    "published_date": {"$date_after": "2024-01-01"}
                },
                "description": "Seminal papers published after 2024-01-01"
            },
            {
                "name": "High Citation Range",
                "filter": {"citations": {"$gte": 700, "$lte": 1500}},
                "description": "Papers with 700-1500 citations"
            },
            {
                "name": "NLP or RL Papers",
                "filter": {"category": {"$in": ["NLP", "RL"]}},
                "description": "Papers in NLP or RL categories"
            },
            {
                "name": "Contains 'vision' Tag",
                "filter": {"tags": {"$contains": "vision"}},
                "description": "Papers with tags containing 'vision'"
            }
        ]
        
        print("Testing Advanced Metadata Filters:\n")
        
        for example in filter_examples:
            print(f"Filter: {example['name']}")
            print(f"Description: {example['description']}")
            print(f"Condition: {example['filter']}")
            
            results = client.search(
                library_id=library.id,
                query_embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
                k=10,
                metadata_filter=example['filter']
            )
            
            print(f"Results: {len(results)} matches")
            for i, result in enumerate(results, 1):
                metadata = result.chunk.metadata
                print(f"  {i}. {metadata.get('category', 'N/A')} - {metadata.get('author', {}).get('name', 'N/A')} ({metadata.get('rating', 'N/A')}⭐)")
            print()
        
        print("✅ Advanced filtering example completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.close()


def bulk_operations_example():
    """Bulk operations example"""
    print("\n📦 Bulk Operations Example\n")
    
    client = StackAIClient(base_url="http://localhost:8000")
    
    try:
        # Create library with multiple documents at once
        documents_data = [
            {
                "title": "Introduction to Machine Learning",
                "metadata": {"course": "CS101", "semester": "Fall 2024"},
                "chunks": [
                    {"text": "Machine learning is a subset of AI.", "metadata": {"chapter": 1}},
                    {"text": "Supervised learning uses labeled data.", "metadata": {"chapter": 2}},
                ]
            },
            {
                "title": "Deep Learning Fundamentals",
                "metadata": {"course": "CS201", "semester": "Fall 2024"},
                "chunks": [
                    {"text": "Neural networks mimic brain structure.", "metadata": {"chapter": 1}},
                    {"text": "Backpropagation trains neural networks.", "metadata": {"chapter": 2}},
                ]
            }
        ]
        
        print("Creating library with bulk documents...")
        library = client.create_library_with_documents(
            library_name="AI Course Materials",
            documents=documents_data,
            library_description="Course materials for AI classes",
            auto_embed=False,  # Use manual embeddings for demo
            index_type="brute_force"
        )
        
        print(f"✅ Created library: {library.name}")
        
        # Verify contents
        documents = client.list_documents(library.id)
        chunks = client.list_chunks_by_library(library.id)
        
        print(f"   Documents: {len(documents)}")
        print(f"   Chunks: {len(chunks)}")
        
        # Bulk search queries
        print("\nPerforming bulk searches...")
        queries = [
            {"query_embedding": [0.1, 0.2, 0.3, 0.4, 0.5], "k": 2},
            {"query_embedding": [0.2, 0.3, 0.4, 0.5, 0.6], "k": 1, "metadata_filter": {"chapter": 1}},
            {"query_embedding": [0.3, 0.4, 0.5, 0.6, 0.7], "k": 3, "similarity_metric": "euclidean"}
        ]
        
        bulk_results = client.bulk_search(library.id, queries)
        
        for i, results in enumerate(bulk_results, 1):
            print(f"   Query {i}: {len(results)} results")
        
        print("\n✅ Bulk operations example completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.close()


if __name__ == "__main__":
    print("🎯 StackAI SDK Examples\n")
    print("Make sure the StackAI API is running on http://localhost:8000\n")
    
    # Run examples
    basic_example()
    advanced_metadata_filtering_example()
    bulk_operations_example()
    
    print("\n🎉 All examples completed!")
    print("\n📚 For more information, see the SDK documentation.") 