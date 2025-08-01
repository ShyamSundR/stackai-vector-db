from typing import Any, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from datetime import datetime
from .chunk import Chunk


class DocumentBase(BaseModel):
    """Base document model with common fields"""
    title: str = Field(..., min_length=1, description="Document title")
    content: Optional[str] = Field(None, description="Full document content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DocumentCreate(DocumentBase):
    """Schema for creating a new document"""
    library_id: UUID = Field(..., description="ID of the library this document belongs to")


class DocumentUpdate(BaseModel):
    """Schema for updating an existing document"""
    title: Optional[str] = Field(None, min_length=1, description="Updated title")
    content: Optional[str] = Field(None, description="Updated content")
    metadata: Optional[dict[str, Any]] = Field(None, description="Updated metadata")


class Document(DocumentBase):
    """Full document model with all fields"""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the document")
    library_id: UUID = Field(..., description="ID of the library this document belongs to")
    chunks: list[Chunk] = Field(default_factory=list, description="Chunks belonging to this document")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True