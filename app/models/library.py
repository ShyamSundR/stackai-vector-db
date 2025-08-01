from typing import Any, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from datetime import datetime


class CreateLibrary(BaseModel):
    """Schema for creating a new library"""
    name: str = Field(..., min_length=1, description="Library name")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class UpdateLibrary(BaseModel):
    """Schema for updating an existing library"""
    name: Optional[str] = Field(None, min_length=1, description="Updated name")
    metadata: Optional[dict[str, Any]] = Field(None, description="Updated metadata")


class Library(BaseModel):
    """Full library model with all fields"""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the library")
    name: str = Field(..., min_length=1, description="Library name")
    documents: list["Document"] = Field(default_factory=list, description="Documents in this library")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    class Config:
        from_attributes = True


# Forward reference resolution
from .document import Document
Library.model_rebuild()
