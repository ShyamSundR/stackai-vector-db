from typing import Optional
from uuid import UUID
from app.models import Library, CreateLibrary, UpdateLibrary
from datetime import datetime


class LibraryService:
    """Service layer for library operations"""
    
    def __init__(self):
        # In-memory storage for now - will be replaced with proper persistence
        self._libraries: dict[UUID, Library] = {}
    
    async def create_library(self, library_data: CreateLibrary) -> Library:
        """Create a new library"""
        lib = Library(**library_data.dict())
        self._libraries[lib.id] = lib
        return lib
    
    async def get_library(self, library_id: UUID) -> Optional[Library]:
        """Get a library by ID"""
        return self._libraries.get(library_id)
    
    async def get_all_libraries(self) -> list[Library]:
        """Get all libraries"""
        return list(self._libraries.values())
    
    async def update_library(self, library_id: UUID, library_data: UpdateLibrary) -> Optional[Library]:
        """Update a library"""
        lib = self._libraries.get(library_id)
        if not lib:
            return None
        update_data = library_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(lib, key, value)
        self._libraries[library_id] = lib
        return lib
    
    async def delete_library(self, library_id: UUID) -> bool:
        """Delete a library"""
        return self._libraries.pop(library_id, None) is not None