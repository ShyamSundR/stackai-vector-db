"""
Data models for StackAI SDK
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID


@dataclass
class Library:
    """Represents a library in StackAI Vector Database"""
    id: str
    name: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @property
    def description(self) -> str:
        """Get description from metadata"""
        return self.metadata.get('description', '')
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Library':
        created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        updated_at = None
        if 'updated_at' in data and data['updated_at']:
            updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
        
        return cls(
            id=data['id'],
            name=data['name'],
            metadata=data.get('metadata', {}),
            created_at=created_at,
            updated_at=updated_at
        )


@dataclass
class Document:
    """Represents a document in StackAI Vector Database"""
    id: str
    title: str
    library_id: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Document':
        created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        updated_at = None
        if 'updated_at' in data and data['updated_at']:
            updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
        
        return cls(
            id=data['id'],
            title=data['title'], 
            library_id=data['library_id'],
            metadata=data.get('metadata', {}),
            created_at=created_at,
            updated_at=updated_at
        )


@dataclass
class Chunk:
    """Represents a chunk in StackAI Vector Database"""
    id: str
    document_id: str
    text: str
    embedding: Optional[List[float]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Chunk':
        created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
        
        return cls(
            id=data['id'],
            document_id=data['document_id'],
            text=data['text'],
            embedding=data.get('embedding'),
            metadata=data.get('metadata', {}),
            created_at=created_at,
            updated_at=updated_at
        )


@dataclass
class SearchResult:
    """Represents a search result from vector similarity search"""
    chunk: Chunk
    distance: float
    similarity: float
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SearchResult':
        return cls(
            chunk=Chunk.from_dict(data['chunk']),
            distance=data['distance'],
            similarity=data['similarity']
        )


@dataclass
class IndexInfo:
    """Information about a vector index"""
    status: str
    index_type: str
    message: str
    
    @classmethod
    def from_dict(cls, data: dict) -> 'IndexInfo':
        return cls(
            status=data['status'],
            index_type=data['index_type'],
            message=data['message']
        )


@dataclass
class HealthStatus:
    """Health status of the API"""
    status: str
    app: str
    version: str
    services: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'HealthStatus':
        return cls(
            status=data['status'],
            app=data['app'],
            version=data['version'],
            services=data.get('services', {})
        ) 