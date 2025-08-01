#!/usr/bin/env python3
"""
Advanced Metadata Filtering Test Suite
Tests the enhanced metadata filtering capabilities of StackAI Vector Database
"""

import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8000/api/v1"

def wait_for_api():
    """Wait for API to be available"""
    for _ in range(30):
        try:
            response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
            if response.status_code == 200:
                print("✅ API is ready")
                return True
        except:
            pass
        time.sleep(1)
    return False

def test_advanced_metadata_filtering():
    """Test advanced metadata filtering capabilities"""
    
    print("🧪 Testing Advanced Metadata Filtering...\n")
    
    if not wait_for_api():
        print("❌ API not available")
        return
    
    # Create library
    library_data = {
        "name": "Advanced Filtering Test Library",
        "description": "Testing advanced metadata filtering features"
    }
    response = requests.post(f"{BASE_URL}/libraries/", json=library_data)
    library_id = response.json()["id"]
    print(f"✅ Library created: {library_id}")
    
    # Create document
    doc_data = {
        "title": "Advanced Filtering Test Document",
        "library_id": library_id
    }
    response = requests.post(f"{BASE_URL}/documents/", json=doc_data)
    document_id = response.json()["id"]
    print(f"✅ Document created: {document_id}")
    
    # Create chunks with rich metadata
    chunks_data = [
        {
            "text": "Machine learning algorithms for healthcare applications",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "metadata": {
                "category": "healthcare",
                "author": {
                    "name": "Dr. Smith",
                    "department": "AI Research"
                },
                "tags": ["ML", "healthcare", "algorithms"],
                "publication_date": "2024-01-15",
                "rating": 4.5,
                "word_count": 1250,
                "is_published": True,
                "research_phase": "production"
            }
        },
        {
            "text": "Deep learning applications in finance sector",
            "embedding": [0.2, 0.3, 0.4, 0.5, 0.6],
            "metadata": {
                "category": "finance",
                "author": {
                    "name": "Prof. Johnson",
                    "department": "Finance"
                },
                "tags": ["DL", "finance", "applications"],
                "publication_date": "2024-02-20",
                "rating": 3.8,
                "word_count": 890,
                "is_published": False,
                "research_phase": "development"
            }
        },
        {
            "text": "Natural language processing for customer service",
            "embedding": [0.3, 0.4, 0.5, 0.6, 0.7],
            "metadata": {
                "category": "customer_service",
                "author": {
                    "name": "Dr. Smith",
                    "department": "AI Research"
                },
                "tags": ["NLP", "customer_service", "automation"],
                "publication_date": "2024-03-10",
                "rating": 4.2,
                "word_count": 1500,
                "is_published": True,
                "research_phase": "production"
            }
        },
        {
            "text": "Computer vision in autonomous vehicles",
            "embedding": [0.4, 0.5, 0.6, 0.7, 0.8],
            "metadata": {
                "category": "automotive",
                "author": {
                    "name": "Dr. Lee",
                    "department": "Computer Vision"
                },
                "tags": ["CV", "automotive", "autonomous"],
                "publication_date": "2023-12-05",
                "rating": 4.9,
                "word_count": 2100,
                "is_published": True,
                "research_phase": "testing"
            }
        }
    ]
    
    # Create chunks
    chunk_ids = []
    for chunk_data in chunks_data:
        response = requests.post(
            f"{BASE_URL}/chunks/",
            json=chunk_data,
            params={"document_id": document_id}
        )
        chunk_ids.append(response.json()["id"])
    
    print(f"✅ Created {len(chunk_ids)} chunks with rich metadata")
    
    # Build index
    response = requests.post(
        f"{BASE_URL}/search/libraries/{library_id}/index",
        params={"index_type": "brute_force"}
    )
    print("✅ Index built successfully")
    
    # Test cases for advanced metadata filtering
    test_cases = [
        {
            "name": "Simple Equality Filter",
            "filter": {"category": "healthcare"},
            "expected_count": 1,
            "description": "Find chunks in healthcare category"
        },
        {
            "name": "Nested Field Access",
            "filter": {"author.name": "Dr. Smith"},
            "expected_count": 2,
            "description": "Find chunks by specific author using nested field"
        },
        {
            "name": "Numeric Comparison - Greater Than",
            "filter": {"rating": {"$gt": 4.0}},
            "expected_count": 3,
            "description": "Find chunks with rating > 4.0"
        },
        {
            "name": "Numeric Range",
            "filter": {"word_count": {"$gte": 1000, "$lte": 1500}},
            "expected_count": 2,
            "description": "Find chunks with word count between 1000-1500"
        },
        {
            "name": "Array Contains",
            "filter": {"tags": {"$in": ["healthcare", "finance"]}},
            "expected_count": 2,
            "description": "Find chunks with healthcare or finance tags"
        },
        {
            "name": "String Contains",
            "filter": {"author.department": {"$contains": "AI"}},
            "expected_count": 2,
            "description": "Find chunks from departments containing 'AI'"
        },
        {
            "name": "Boolean Filter",
            "filter": {"is_published": True},
            "expected_count": 3,
            "description": "Find published chunks"
        },
        {
            "name": "Date After Filter",
            "filter": {"publication_date": {"$date_after": "2024-01-01"}},
            "expected_count": 3,
            "description": "Find chunks published after 2024-01-01"
        },
        {
            "name": "Date Range Filter",
            "filter": {"publication_date": {"$date_range": {"start": "2024-01-01", "end": "2024-02-28"}}},
            "expected_count": 2,
            "description": "Find chunks published in Jan-Feb 2024"
        },
        {
            "name": "Regular Expression",
            "filter": {"research_phase": {"$regex": "^prod"}},
            "expected_count": 2,
            "description": "Find chunks in production phase (starts with 'prod')"
        },
        {
            "name": "Field Exists",
            "filter": {"rating": {"$exists": True}},
            "expected_count": 4,
            "description": "Find chunks that have a rating field"
        },
        {
            "name": "Complex Multi-Condition",
            "filter": {
                "category": {"$ne": "finance"},
                "rating": {"$gte": 4.0},
                "is_published": True
            },
            "expected_count": 2,
            "description": "Find published, highly-rated non-finance chunks"
        }
    ]
    
    print("\n🔍 Running Advanced Metadata Filtering Tests...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        print(f"   Filter: {json.dumps(test_case['filter'], indent=2)}")
        
        # Perform search with metadata filter
        search_request = {
            "query_embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "k": 10,
            "metadata_filter": test_case['filter']
        }
        
        response = requests.post(
            f"{BASE_URL}/search/libraries/{library_id}/search",
            json=search_request
        )
        
        if response.status_code == 200:
            results = response.json()["results"]
            actual_count = len(results)
            
            if actual_count == test_case["expected_count"]:
                print(f"   ✅ PASS: Found {actual_count} chunks (expected {test_case['expected_count']})")
                
                # Show some result details
                for j, result in enumerate(results[:2]):  # Show first 2 results
                    metadata = result["chunk"]["metadata"]
                    print(f"      Result {j+1}: {metadata.get('category', 'N/A')} - {metadata.get('author', {}).get('name', 'N/A')}")
            else:
                print(f"   ❌ FAIL: Found {actual_count} chunks (expected {test_case['expected_count']})")
        else:
            print(f"   ❌ ERROR: {response.status_code} - {response.text}")
        
        print()
    
    # Performance test
    print("⚡ Performance Test: Complex filter with large result set")
    start_time = time.time()
    
    complex_filter = {
        "rating": {"$gte": 3.0},
        "author.department": {"$contains": "Research"},
        "publication_date": {"$date_after": "2023-01-01"}
    }
    
    search_request = {
        "query_embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
        "k": 10,
        "metadata_filter": complex_filter
    }
    
    response = requests.post(
        f"{BASE_URL}/search/libraries/{library_id}/search",
        json=search_request
    )
    
    end_time = time.time()
    
    if response.status_code == 200:
        results = response.json()["results"]
        print(f"✅ Complex filter completed in {(end_time - start_time)*1000:.2f}ms")
        print(f"   Found {len(results)} matching chunks")
    else:
        print(f"❌ Performance test failed: {response.status_code}")
    
    print("\n🎉 Advanced Metadata Filtering Tests Complete!")
    print("\n📋 Supported Filter Operations:")
    print("  • $eq, $ne - Equality/inequality")
    print("  • $gt, $gte, $lt, $lte - Numeric comparisons") 
    print("  • $in, $nin - Array membership")
    print("  • $contains - String contains (case-insensitive)")
    print("  • $regex - Regular expression matching")
    print("  • $exists - Field existence check")
    print("  • $date_after, $date_before, $date_range - Date comparisons")
    print("  • Nested field access with dot notation (e.g., 'author.name')")
    print("  • Multiple conditions with AND logic")

if __name__ == "__main__":
    test_advanced_metadata_filtering() 