from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from app.models import Library, CreateLibrary, UpdateLibrary
from app.core.dependencies import get_library_repository
from app.repositories.library_repository import LibraryRepository

router = APIRouter()

@router.post("/", response_model=Library, status_code=201)
async def create_library(
    library_data: CreateLibrary,
    repo: LibraryRepository = Depends(get_library_repository)
) -> Library:
    """Create a new library"""
    library = Library(**library_data.dict())
    return repo.create_library(library)

@router.get("/{library_id}", response_model=Library)
async def get_library(
    library_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
) -> Library:
    """Get a library by ID"""
    lib = repo.get_library(library_id)
    if not lib:
        raise HTTPException(status_code=404, detail="Library not found")
    return lib

@router.get("/", response_model=list[Library])
async def get_all_libraries(
    repo: LibraryRepository = Depends(get_library_repository)
) -> list[Library]:
    """Get all libraries"""
    return repo.get_all_libraries()

@router.put("/{library_id}", response_model=Library)
async def update_library(
    library_id: UUID,
    library_data: UpdateLibrary,
    repo: LibraryRepository = Depends(get_library_repository)
) -> Library:
    """Update a library"""
    update_data = library_data.dict(exclude_unset=True)
    lib = repo.update_library(library_id, **update_data)
    if not lib:
        raise HTTPException(status_code=404, detail="Library not found")
    return lib

@router.delete("/{library_id}", status_code=204)
async def delete_library(
    library_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
) -> None:
    """Delete a library"""
    deleted = repo.delete_library(library_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Library not found")
    return None
