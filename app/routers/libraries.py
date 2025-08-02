from fastapi import APIRouter, HTTPException, Depends, status
from uuid import UUID
from app.models import Library, CreateLibrary, UpdateLibrary
from app.services.library_service import LibraryService
from app.core.dependencies import get_library_service

router = APIRouter()

@router.post("/", response_model=Library, status_code=status.HTTP_201_CREATED)
async def create_library(
    library_data: CreateLibrary,
    service: LibraryService = Depends(get_library_service)
):
    """Create a new library"""
    try:
        library = await service.create_library(library_data)
        return library
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{library_id}", response_model=Library)
async def get_library(
    library_id: UUID,
    service: LibraryService = Depends(get_library_service)
):
    """Get a library by ID"""
    library = await service.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Library not found"
        )
    return library

@router.get("/", response_model=list[Library])
async def list_libraries(
    service: LibraryService = Depends(get_library_service)
):
    """List all libraries"""
    return await service.get_all_libraries()

@router.put("/{library_id}", response_model=Library)
async def update_library(
    library_id: UUID,
    update_data: UpdateLibrary,
    service: LibraryService = Depends(get_library_service)
):
    """Update a library"""
    try:
        library = await service.update_library(library_id, update_data)
        if not library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Library not found"
            )
        return library
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library(
    library_id: UUID,
    service: LibraryService = Depends(get_library_service)
):
    """Delete a library"""
    success = await service.delete_library(library_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Library not found"
        )
    return None
