from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from uuid import UUID
from app.models import Document, DocumentCreate, DocumentUpdate
from app.services.document_service import DocumentService
from app.core.dependencies import get_document_service

router = APIRouter()

@router.post("/", response_model=Document, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    service: DocumentService = Depends(get_document_service)
):
    """Create a new document"""
    try:
        document = await service.create_document(document_data)
        return document
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """Get a document by ID"""
    document = await service.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

@router.get("/", response_model=List[Document])
async def get_documents_by_library(
    library_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """Get all documents in a library"""
    try:
        return await service.get_documents_by_library(library_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{document_id}", response_model=Document)
async def update_document(
    document_id: UUID,
    document_data: DocumentUpdate,
    service: DocumentService = Depends(get_document_service)
):
    """Update a document"""
    try:
        document = await service.update_document(document_id, document_data)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return document
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """Delete a document"""
    success = await service.delete_document(document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return None