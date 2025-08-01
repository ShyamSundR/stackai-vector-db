import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Cohere API configuration
    COHERE_API_KEY: Optional[str] = os.getenv("COHERE_API_KEY")
    COHERE_MODEL: str = os.getenv("COHERE_MODEL", "embed-english-v3.0")
    
    # Application settings
    APP_NAME: str = "StackAI Vector Database"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # API Configuration
    api_title: str = "Vector Database API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # Vector Search Configuration
    default_k: int = 10
    max_k: int = 100
    similarity_threshold: float = 0.0
    
    # Performance Configuration
    max_embedding_dimension: int = 1536  # OpenAI embedding dimension
    max_chunks_per_library: int = 100000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()