from typing import Optional, List
from uuid import UUID
from app.models import Library, CreateLibrary, UpdateLibrary
from app.repositories.library_repository import LibraryRepository


class LibraryService:
    """Service layer for library operations with business logic"""
    
    def __init__(self, repository: LibraryRepository):
        self._repository = repository
    
    async def create_library(self, library_data: CreateLibrary) -> Library:
        """Create a new library with business validation"""
        # Business logic validation
        if len(library_data.name.strip()) < 3:
            raise ValueError("Library name must be at least 3 characters long")
        
        if library_data.name.strip() != library_data.name:
            raise ValueError("Library name cannot have leading or trailing whitespace")
        
        # Check for duplicate names
        existing_libraries = self._repository.get_all_libraries()
        for lib in existing_libraries:
            if lib.name.lower() == library_data.name.lower():
                raise ValueError(f"Library with name '{library_data.name}' already exists")
        
        # Delegate to repository
        return self._repository.create_library(library_data)
    
    async def get_library(self, library_id: UUID) -> Optional[Library]:
        """Get a library by ID"""
        return self._repository.get_library(library_id)
    
    async def get_all_libraries(self) -> List[Library]:
        """Get all libraries"""
        return self._repository.get_all_libraries()
    
    async def update_library(self, library_id: UUID, library_data: UpdateLibrary) -> Optional[Library]:
        """Update a library with business validation"""
        # Check if library exists
        existing_library = self._repository.get_library(library_id)
        if not existing_library:
            return None
        
        # Business logic validation
        if library_data.name and len(library_data.name.strip()) < 3:
            raise ValueError("Library name must be at least 3 characters long")
        
        if library_data.name and library_data.name.strip() != library_data.name:
            raise ValueError("Library name cannot have leading or trailing whitespace")
        
        # Check for duplicate names (excluding current library)
        if library_data.name:
            existing_libraries = self._repository.get_all_libraries()
            for lib in existing_libraries:
                if lib.id != library_id and lib.name.lower() == library_data.name.lower():
                    raise ValueError(f"Library with name '{library_data.name}' already exists")
        
        # Delegate to repository
        return self._repository.update_library(library_id, **library_data.dict(exclude_unset=True))
    
    async def delete_library(self, library_id: UUID) -> bool:
        """Delete a library with business logic checks"""
        # Check if library exists
        existing_library = self._repository.get_library(library_id)
        if not existing_library:
            return False
        
        # Business logic: Could add checks here like:
        # - Prevent deletion if library has important documents
        # - Log deletion for audit purposes
        # - Send notifications
        
        # Delegate to repository
        return self._repository.delete_library(library_id)