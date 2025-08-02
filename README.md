# StackAI Vector Database

A high-performance REST API for vector database operations with perfect Domain-Driven Design (DDD) architecture. Supports both manual embeddings and automatic embedding generation via Cohere API. Built with FastAPI and custom indexing algorithms.

## Architecture & Design

**Perfect Domain-Driven Design Implementation**:
- **API Layer**: FastAPI routers handle HTTP requests and delegate to services
- **Service Layer**: Business logic, validation, and orchestration
- **Repository Layer**: Thread-safe data access and storage management
- **Clean Separation**: API → Service → Repository (never API → Repository)

## Features

### Core Functionality
- **Library Management**: Create and organize document collections with validation
- **Document Storage**: Manage documents within libraries with business rules
- **Chunk Operations**: Handle text segments with embeddings, metadata, and validation
- **Vector Search**: k-Nearest Neighbor similarity search with filtering
- **Multiple Index Types**: Brute-force and KD-Tree implementations
- **Thread Safety**: Concurrent operations with proper locking mechanisms

### Business Logic & Validation
- **Input Validation**: Name/title length, whitespace handling, content size limits
- **Business Rules**: Duplicate checking, referential integrity validation
- **Entity Relationships**: Library-document-chunk hierarchy enforcement
- **Error Handling**: Comprehensive validation with descriptive HTTP error responses
- **Data Integrity**: Cascading operations and relationship consistency

### DDD Architecture Benefits
- **Maintainability**: Clear separation between API, business logic, and data access
- **Testability**: Business logic isolated in services for comprehensive unit testing
- **Scalability**: Service layer can be easily extracted to microservices
- **Extensibility**: New business rules can be added without touching API or data layers
- **Code Quality**: Enterprise-grade patterns following SOLID principles

**Example Business Validations**:
```python
# Library names must be at least 3 characters
# Document titles cannot have leading/trailing whitespace  
# Chunk content cannot exceed 10,000 characters
# Duplicate names/titles prevented within scope
# Referential integrity enforced (library → document → chunk)
```

### Embedding Support
- **Auto-Embedding**: Generate embeddings automatically using Cohere API
- **Manual Embeddings**: Support for pre-computed embedding vectors
- **Flexible Input**: Mix manual and auto-generated embeddings
- **Multiple Models**: Support for different Cohere embedding models

### Search & Indexing
- **Multiple Algorithms**: Choose between brute-force and KD-Tree indexing
- **Similarity Metrics**: Cosine similarity, Euclidean distance, dot product
- **Metadata Filtering**: Filter search results by chunk metadata
- **Dynamic Indexing**: Switch index types and rebuild on demand

### Extra Features (Production Enhancements)

#### 1. Advanced Metadata Filtering
- **12+ Filter Operators**: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$contains`, `$regex`, `$exists`, `$date_after`, `$date_before`, `$date_range`
- **Nested Field Access**: Use dot notation (e.g., `author.name`, `user.profile.email`)
- **Complex Conditions**: Multi-condition AND logic with mixed operators
- **Date Parsing**: Support for ISO, common date formats with intelligent parsing
- **Performance Optimized**: Smart pre-filtering with 3x result expansion
- **Type Safety**: Handles strings, numbers, booleans, arrays, dates seamlessly

#### 2. Python SDK Client
- **Complete API Coverage**: Full CRUD operations for Libraries, Documents, Chunks
- **Professional Architecture**: Dataclass models, exception hierarchy, type hints
- **Advanced Search**: Vector similarity with metadata filtering and auto-embedding
- **Bulk Operations**: Create libraries with documents and chunks in one call
- **Error Handling**: Comprehensive exception handling with detailed error messages
- **Easy Installation**: `pip install stackai-sdk` (or local setup with `setup.py`)
- **Rich Examples**: Comprehensive usage examples and documentation

## Quick Start

### Option 1: Docker (Recommended)

1. **Clone and build:**
   ```bash
   git clone <repository>
   cd stackai
   docker build -t stackai .
   ```

2. **Run with environment variables:**
   ```bash
   docker run -p 8000:8000 \
     -e COHERE_API_KEY=your_cohere_api_key \
     -e COHERE_MODEL=embed-english-v3.0 \
     stackai
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Option 2: Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export COHERE_API_KEY=your_cohere_api_key
   export COHERE_MODEL=embed-english-v3.0
   ```

3. **Run the server:**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## API Usage Examples

### 1. Create a Library
```bash
curl -X POST "http://localhost:8000/api/v1/libraries/" \
  -H "Content-Type: application/json" \
  -d '{"name": "AI Research Papers", "metadata": {"domain": "machine_learning"}}'
```

### 2. Create a Document  
```bash
curl -X POST "http://localhost:8000/api/v1/documents/" \
  -H "Content-Type: application/json" \
  -d '{"title": "Attention Is All You Need", "library_id": "library-uuid", "metadata": {"authors": ["Vaswani", "Shazeer"], "year": 2017}}'
```

### 3. Add Chunks with Auto-Embedding
```bash
curl -X POST "http://localhost:8000/api/v1/chunks/?document_id=doc-uuid" \
  -H "Content-Type: application/json" \
  -d '{"text": "Transformers have revolutionized natural language processing", "auto_embed": true, "metadata": {"section": "introduction", "page": 1}}'
```

### 4. Add Chunks with Manual Embedding
```bash
curl -X POST "http://localhost:8000/api/v1/chunks/?document_id=doc-uuid" \
  -H "Content-Type: application/json" \
  -d '{"text": "Manual embedding example", "embedding": [0.1, 0.2, 0.3, ...], "metadata": {"source": "openai"}}'
```

### 5. Build Vector Index
```bash
curl -X POST "http://localhost:8000/api/v1/search/libraries/library-uuid/index?index_type=brute_force"
```

### 6. Search with Auto-Embedding
```bash
curl -X POST "http://localhost:8000/api/v1/search/libraries/library-uuid/search" \
  -H "Content-Type: application/json" \
  -d '{"query_text": "transformer architecture attention mechanism", "k": 5, "similarity_metric": "cosine"}'
```

### 7. Search with Manual Embedding
```bash
curl -X POST "http://localhost:8000/api/v1/search/libraries/library-uuid/search" \
  -H "Content-Type: application/json" \
  -d '{"query_embedding": [0.1, 0.2, 0.3, ...], "k": 5, "similarity_metric": "cosine"}'
```

### 8. Advanced Metadata Filtering
```bash
curl -X POST "http://localhost:8000/api/v1/search/libraries/library-uuid/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "neural networks", 
    "k": 10,
    "metadata_filter": {
      "year": {"$gte": 2020},
      "authors": {"$in": ["Vaswani", "Devlin"]},
      "section": {"$ne": "references"}
    }
  }'
```

## Python SDK Usage

```python
from stackai_sdk import StackAIClient

# Initialize client
client = StackAIClient(base_url="http://localhost:8000")

# Create library
library = client.create_library("AI Research", {"domain": "ML"})

# Create document  
doc = client.create_document("Transformer Paper", library.id, {"year": 2017})

# Add chunk with auto-embedding
chunk = client.create_chunk(
    "Attention mechanisms allow models to focus on relevant parts",
    doc.id, 
    auto_embed=True,
    metadata={"section": "background"}
)

# Search with auto-embedding
results = client.search_library(
    library.id,
    query_text="attention mechanism transformer",
    k=5,
    metadata_filter={"section": {"$ne": "references"}}
)

for result in results:
    print(f"Score: {result.similarity:.3f} - {result.chunk.text[:100]}")
```

## Architecture

The system follows a layered architecture with clear separation of concerns:

- **API Layer**: FastAPI routers handling HTTP requests/responses
- **Service Layer**: Business logic and orchestration
- **Repository Layer**: Data access and storage  
- **Index Layer**: Vector search implementations
- **Model Layer**: Pydantic data models and validation

Key design patterns:
- Repository pattern for data access
- Dependency injection for loose coupling
- Strategy pattern for pluggable index algorithms
- Thread-safe operations with RLock

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Quality
```bash
# Format code
black .
isort .

# Lint
flake8 .

# Type checking  
mypy app/
```

### Docker Development
```bash
# Build development image
docker build -t stackai:dev .

# Run with mounted code
docker run -p 8000:8000 -v $(pwd):/app stackai:dev
```

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `COHERE_API_KEY` | Cohere API key for embeddings | Required for auto-embed |
| `COHERE_MODEL` | Cohere model name | `embed-english-v3.0` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

## Performance Characteristics

### Index Algorithms
- **Brute Force**: O(n) search, optimal for small datasets (<10K chunks)
- **KD-Tree**: O(log n) search, better for larger datasets, limited by dimensionality

### Similarity Metrics
- **Cosine**: Measures angle between vectors, good for text embeddings
- **Euclidean**: L2 distance, sensitive to vector magnitude  
- **Dot Product**: Fast computation, assumes normalized vectors

### Metadata Filtering
- Pre-filtering with result expansion for optimal performance
- Smart operator selection based on data types
- Lazy evaluation for complex nested conditions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.