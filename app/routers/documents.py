from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from app.models import Document, DocumentCreate, DocumentUpdate
from app.core.dependencies import get_library_repository
from app.repositories.library_repository import LibraryRepository

router = APIRouter(tags=["documents"])

@router.post("/", response_model=Document, status_code=201)
async def create_document(document_data: DocumentCreate, repo: LibraryRepository = Depends(get_library_repository)):
    document = Document(**document_data.dict())
    result = repo.create_document(document, document_data.library_id)
    if not result:
        raise HTTPException(status_code=404, detail="Library not found")
    return result

@router.get("/{document_id}", response_model=Document)
async def get_document(document_id: UUID, repo: LibraryRepository = Depends(get_library_repository)):
    doc = repo.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/library/{library_id}", response_model=list[Document])
async def get_documents_by_library(library_id: UUID, repo: LibraryRepository = Depends(get_library_repository)):
    return repo.get_library_documents(library_id)

@router.put("/{document_id}", response_model=Document)
async def update_document(document_id: UUID, document_data: DocumentUpdate, repo: LibraryRepository = Depends(get_library_repository)):
    update_data = document_data.dict(exclude_unset=True)
    doc = repo.update_document(document_id, **update_data)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: UUID, repo: LibraryRepository = Depends(get_library_repository)):
    deleted = repo.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return None