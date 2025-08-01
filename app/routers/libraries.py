from fastapi import APIRouter, HTTPException, Depends, status
from uuid import UUID
from app.models import Library, CreateLibrary, UpdateLibrary
from app.repositories.library_repository import LibraryRepository
from app.core.dependencies import get_library_repository

router = APIRouter()

@router.post("/", response_model=Library, status_code=status.HTTP_201_CREATED)
async def create_library(
    library_data: CreateLibrary,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Create a new library"""
    library = repo.create_library(library_data)
    return library

@router.get("/{library_id}", response_model=Library)
async def get_library(
    library_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Get a library by ID"""
    library = repo.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Library not found"
        )
    return library

@router.get("/", response_model=list[Library])
async def list_libraries(
    repo: LibraryRepository = Depends(get_library_repository)
):
    """List all libraries"""
    return repo.get_all_libraries()

@router.put("/{library_id}", response_model=Library)
async def update_library(
    library_id: UUID,
    update_data: UpdateLibrary,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Update a library"""
    library = repo.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Library not found"
        )
    return repo.update_library(library_id, update_data)

@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library(
    library_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Delete a library"""
    library = repo.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Library not found"
        )
    repo.delete_library(library_id)
    return None
