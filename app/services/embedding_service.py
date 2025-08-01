import cohere
from typing import List, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using Cohere API"""
    
    def __init__(self):
        self.client: Optional[cohere.Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Cohere client if API key is available"""
        if settings.COHERE_API_KEY:
            try:
                self.client = cohere.Client(settings.COHERE_API_KEY)
                logger.info("Cohere client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Cohere client: {e}")
                self.client = None
        else:
            logger.warning("No Cohere API key provided. Embedding generation will not be available.")
    
    def is_available(self) -> bool:
        """Check if embedding service is available"""
        return self.client is not None
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            ValueError: If service is not available or text is empty
            Exception: If API call fails
        """
        if not self.is_available():
            raise ValueError("Embedding service not available. Please check your Cohere API key.")
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            response = self.client.embed(
                texts=[text.strip()],
                model=settings.COHERE_MODEL,
                input_type="search_document"
            )
            
            return response.embeddings[0]
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise Exception(f"Embedding generation failed: {str(e)}")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embedding vectors
            
        Raises:
            ValueError: If service is not available or texts list is empty
            Exception: If API call fails
        """
        if not self.is_available():
            raise ValueError("Embedding service not available. Please check your Cohere API key.")
        
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        # Filter out empty texts
        filtered_texts = [text.strip() for text in texts if text and text.strip()]
        
        if not filtered_texts:
            raise ValueError("All texts are empty")
        
        try:
            response = self.client.embed(
                texts=filtered_texts,
                model=settings.COHERE_MODEL,
                input_type="search_document"
            )
            
            return response.embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise Exception(f"Embeddings generation failed: {str(e)}")
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query
        
        Args:
            query: Search query text
            
        Returns:
            List of floats representing the query embedding vector
            
        Raises:
            ValueError: If service is not available or query is empty
            Exception: If API call fails
        """
        if not self.is_available():
            raise ValueError("Embedding service not available. Please check your Cohere API key.")
        
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        try:
            response = self.client.embed(
                texts=[query.strip()],
                model=settings.COHERE_MODEL,
                input_type="search_query"
            )
            
            return response.embeddings[0]
            
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            raise Exception(f"Query embedding generation failed: {str(e)}")

# Global instance
embedding_service = EmbeddingService() 