from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import libraries, documents, chunks, search
from app.services.embedding_service import embedding_service

app = FastAPI(
    title="StackAI Vector Database", 
    description="A vector database API for indexing and searching document chunks with embedding support",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(libraries.router, prefix="/api/v1/libraries", tags=["libraries"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(chunks.router, prefix="/api/v1/chunks", tags=["chunks"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])

@app.get("/health")
async def health_check():
    """Health check endpoint with service status"""
    return {
        "status": "healthy",
        "app": "StackAI Vector Database",
        "version": "1.0.0",
        "services": {
            "embedding_service": {
                "available": embedding_service.is_available(),
                "cohere_configured": embedding_service.client is not None,
                "model": "embed-english-v3.0" if embedding_service.is_available() else None
            }
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to StackAI Vector Database API",
        "docs": "/docs",
        "health": "/health",
        "embedding_status": "/api/v1/search/embedding/status"
    }