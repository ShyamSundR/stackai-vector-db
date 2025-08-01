from fastapi import APIRouter, HTTPException, Depends, status
from uuid import UUID
from app.models import Document, DocumentCreate, DocumentUpdate
from app.repositories.library_repository import LibraryRepository
from app.core.dependencies import get_library_repository

router = APIRouter()

@router.post("/", response_model=Document, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Create a new document in a library"""
    library = repo.get_library(document_data.library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Library not found"
        )
    return repo.create_document(document_data)

@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Get a document by ID"""
    document = repo.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Document not found"
        )
    return document

@router.get("/library/{library_id}", response_model=list[Document])
async def get_documents_by_library(library_id: UUID, repo: LibraryRepository = Depends(get_library_repository)):
    return repo.get_library_documents(library_id)

@router.put("/{document_id}", response_model=Document)
async def update_document(
    document_id: UUID,
    update_data: DocumentUpdate,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Update a document"""
    document = repo.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Document not found"
        )
    return repo.update_document(document_id, update_data)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    repo: LibraryRepository = Depends(get_library_repository)
):
    """Delete a document"""
    document = repo.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Document not found"
        )
    repo.delete_document(document_id)
    return None