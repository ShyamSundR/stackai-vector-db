from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime


class Chunk(BaseModel):
    """Chunk model representing a text segment with embedding and metadata"""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the chunk")
    document_id: UUID = Field(description="ID of the document this chunk belongs to")
    text: str = Field(description="Text content of the chunk")
    embedding: List[float] = Field(description="Vector embedding of the text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CreateChunk(BaseModel):
    """Model for creating a new chunk"""
    text: str = Field(description="Text content of the chunk")
    embedding: Optional[List[float]] = Field(
        default=None, 
        description="Vector embedding of the text. If not provided and auto_embed=True, will be generated via Cohere API"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    auto_embed: bool = Field(
        default=False,
        description="Whether to automatically generate embedding using Cohere API if embedding is not provided"
    )


class UpdateChunk(BaseModel):
    """Model for updating a chunk"""
    text: Optional[str] = Field(default=None, description="Text content of the chunk")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding of the text")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    auto_embed: bool = Field(
        default=False,
        description="Whether to automatically regenerate embedding using Cohere API if text is updated"
    )