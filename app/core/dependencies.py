from app.repositories.library_repository import LibraryRepository

# Singleton repository instance shared across all routers
_library_repo = LibraryRepository()

def get_library_repository() -> LibraryRepository:
    """Get the shared LibraryRepository instance"""
    return _library_repo 