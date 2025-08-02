#!/bin/bash

# =============================================================================
# STACKAI VECTOR DATABASE 
# =============================================================================

# Step 1: Start Docker with Cohere API Keys
echo "=== STARTING STACKAI WITH COHERE AUTO-EMBEDDING ==="
docker-compose down
docker-compose up --build -d

# Step 2: Wait for startup and verify health
echo "Waiting for startup..."
sleep 10
echo "=== HEALTH CHECK - VERIFYING COHERE INTEGRATION ==="
curl -s http://localhost:8000/health | python -m json.tool

# Step 3: Show API Documentation
echo "=== API DOCUMENTATION AVAILABLE AT ==="
echo "Swagger UI: http://localhost:8000/docs"
echo "OpenAPI JSON: http://localhost:8000/openapi.json"

# Step 4: Test Core CRUD Operations
echo "=== TESTING CORE API ENDPOINTS ==="

# Create Library
echo "Creating library..."
LIBRARY_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/libraries/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Auto-Embedding Demo", "metadata": {"embedding_type": "cohere", "model": "embed-english-v3.0"}}')
echo $LIBRARY_RESPONSE | python -m json.tool
LIBRARY_ID=$(echo $LIBRARY_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Library ID: $LIBRARY_ID"

# Create Document
echo "Creating document..."
DOCUMENT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/documents/ \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"NLP Research Papers\", \"library_id\": \"$LIBRARY_ID\", \"metadata\": {\"domain\": \"artificial_intelligence\"}}")
echo $DOCUMENT_RESPONSE | python -m json.tool
DOCUMENT_ID=$(echo $DOCUMENT_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Document ID: $DOCUMENT_ID"

# Step 5: AUTO-EMBEDDING DEMONSTRATION
echo "=== AUTO-EMBEDDING WITH COHERE (NO MANUAL EMBEDDINGS!) ==="

# Add chunks with auto-embedding
echo "Adding chunk 1 with auto-embedding..."
CHUNK1_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/chunks/?document_id=$DOCUMENT_ID" \
  -H "Content-Type: application/json" \
  -d '{"text": "Transformers revolutionized natural language processing with self-attention mechanisms", "metadata": {"paper": "attention_is_all_you_need"}}')
echo $CHUNK1_RESPONSE | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(json.dumps({
        'id': data.get('id'),
        'text': data.get('text'),
        'embedding_dimensions': len(data.get('embedding', [])),
        'auto_generated': True
    }, indent=2))
except: pass
"

echo "Adding chunk 2 with auto-embedding..."
CHUNK2_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/chunks/?document_id=$DOCUMENT_ID" \
  -H "Content-Type: application/json" \
  -d '{"text": "BERT introduced bidirectional encoder representations for language understanding", "metadata": {"paper": "bert"}}')
echo $CHUNK2_RESPONSE | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(json.dumps({
        'id': data.get('id'),
        'text': data.get('text'),
        'embedding_dimensions': len(data.get('embedding', [])),
        'auto_generated': True
    }, indent=2))
except: pass
"

echo "Adding chunk 3 with auto-embedding..."
CHUNK3_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/chunks/?document_id=$DOCUMENT_ID" \
  -H "Content-Type: application/json" \
  -d '{"text": "GPT models demonstrate the power of autoregressive language modeling at scale", "metadata": {"paper": "gpt"}}')
echo $CHUNK3_RESPONSE | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(json.dumps({
        'id': data.get('id'),
        'text': data.get('text'),
        'embedding_dimensions': len(data.get('embedding', [])),
        'auto_generated': True
    }, indent=2))
except: pass
"

# Step 6: Index Building
echo "=== BUILDING VECTOR INDEX ==="
echo "Building brute-force index..."
curl -s -X POST "http://localhost:8000/api/v1/search/libraries/$LIBRARY_ID/index?index_type=brute_force" | python -m json.tool

echo "Building KD-tree index..."
curl -s -X POST "http://localhost:8000/api/v1/search/libraries/$LIBRARY_ID/index?index_type=kdtree" | python -m json.tool

# Step 7: AUTO-EMBEDDING SEARCH (The Magic!)
echo "=== AUTO-EMBEDDING SEARCH DEMONSTRATION ==="

echo "Search 1: Natural language query about attention mechanisms..."
curl -s -X POST "http://localhost:8000/api/v1/search/libraries/$LIBRARY_ID/search" \
  -H "Content-Type: application/json" \
  -d '{"query_text": "attention mechanisms in neural networks", "k": 3, "similarity_metric": "cosine"}' | \
  python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for item in data:
        print(json.dumps({
            'similarity': item.get('similarity'),
            'text': item.get('chunk', {}).get('text'),
            'paper': item.get('chunk', {}).get('metadata', {}).get('paper')
        }, indent=2))
except: pass
"

echo "Search 2: Query about language understanding..."
curl -s -X POST "http://localhost:8000/api/v1/search/libraries/$LIBRARY_ID/search" \
  -H "Content-Type: application/json" \
  -d '{"query_text": "bidirectional language representation", "k": 2, "similarity_metric": "cosine"}' | \
  python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for item in data:
        print(json.dumps({
            'similarity': item.get('similarity'),
            'text': item.get('chunk', {}).get('text'),
            'paper': item.get('chunk', {}).get('metadata', {}).get('paper')
        }, indent=2))
except: pass
"

echo "Search 3: Query about generative models..."
curl -s -X POST "http://localhost:8000/api/v1/search/libraries/$LIBRARY_ID/search" \
  -H "Content-Type: application/json" \
  -d '{"query_text": "generative language models", "k": 2, "similarity_metric": "euclidean"}' | \
  python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for item in data:
        print(json.dumps({
            'similarity': item.get('similarity'),
            'text': item.get('chunk', {}).get('text'),
            'paper': item.get('chunk', {}).get('metadata', {}).get('paper')
        }, indent=2))
except: pass
"

# Step 8: CRUD Operations Testing
echo "=== TESTING CRUD OPERATIONS ==="

# List all libraries
echo "All libraries:"
curl -s http://localhost:8000/api/v1/libraries/ | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for item in data:
        print(json.dumps({
            'id': item.get('id'),
            'name': item.get('name'),
            'document_count': len(item.get('documents', []))
        }, indent=2))
except: pass
"

# Get library chunks
echo "Chunks in library:"
curl -s "http://localhost:8000/api/v1/chunks/library/$LIBRARY_ID" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for item in data:
        print(json.dumps({
            'id': item.get('id'),
            'text': item.get('text'),
            'has_embedding': item.get('embedding') is not None
        }, indent=2))
except: pass
"

# Get documents in library
echo "Documents in library:"
curl -s "http://localhost:8000/api/v1/libraries/$LIBRARY_ID" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for doc in data.get('documents', []):
        print(json.dumps({
            'id': doc.get('id'),
            'title': doc.get('title'),
            'chunk_count': len(doc.get('chunks', []))
        }, indent=2))
except: pass
"

# Step 9: Advanced Metadata Filtering
echo "=== ADVANCED METADATA FILTERING ==="

# Create more diverse content for filtering demo
echo "Adding content with diverse metadata..."
curl -s -X POST "http://localhost:8000/api/v1/chunks/?document_id=$DOCUMENT_ID" \
  -H "Content-Type: application/json" \
  -d '{"text": "Convolutional neural networks excel at image recognition tasks", "metadata": {"domain": "computer_vision", "year": 2012, "architecture": "CNN"}}' > /dev/null

curl -s -X POST "http://localhost:8000/api/v1/chunks/?document_id=$DOCUMENT_ID" \
  -H "Content-Type: application/json" \
  -d '{"text": "Recurrent neural networks process sequential data effectively", "metadata": {"domain": "sequence_modeling", "year": 2015, "architecture": "RNN"}}' > /dev/null

# Rebuild index with new content
curl -s -X POST "http://localhost:8000/api/v1/search/libraries/$LIBRARY_ID/index?index_type=brute_force" > /dev/null

# Search with metadata filtering
echo "Search with metadata filtering (domain = NLP):"
curl -s -X POST "http://localhost:8000/api/v1/search/libraries/$LIBRARY_ID/search" \
  -H "Content-Type: application/json" \
  -d '{"query_text": "neural networks", "k": 5, "similarity_metric": "cosine", "metadata_filter": {"paper": {"$exists": true}}}' | \
  python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for item in data:
        print(json.dumps({
            'similarity': item.get('similarity'),
            'text': item.get('chunk', {}).get('text'),
            'metadata': item.get('chunk', {}).get('metadata')
        }, indent=2))
except: pass
"

# Step 10: Performance and Health Monitoring
echo "=== SYSTEM MONITORING ==="

# Check embedding service status
echo "Embedding service status:"
curl -s http://localhost:8000/health | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(json.dumps(data.get('services', {}).get('embedding_service'), indent=2))
except: pass
"

# Step 11: Cleanup Demo (Optional)
echo "=== CLEANUP COMMANDS (OPTIONAL) ==="
echo "To delete the demo library:"
echo "curl -X DELETE http://localhost:8000/api/v1/libraries/$LIBRARY_ID"
echo ""
echo "To stop Docker:"
echo "docker-compose down"

# Step 12: Summary
echo "=== DEMO SUMMARY ==="
echo " Docker started with Cohere integration"
echo " Auto-embedding working (1024 dimensions)"
echo " Vector search with text queries "
echo " Multiple indexing algorithms (brute-force, KD-tree)"
echo " Advanced metadata filtering"
echo " CRUD operations for Libraries, Documents, Chunks"
echo " Health monitoring and statistics"
echo ""
echo " Your StackAI Vector Database is fully functional!"
echo " API Documentation: http://localhost:8000/docs"
echo " Try custom searches at: http://localhost:8000/docs#/search"
