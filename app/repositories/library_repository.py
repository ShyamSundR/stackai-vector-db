import threading
from typing import Optional, List
from uuid import UUID
from copy import deepcopy
from datetime import datetime

from app.models import Library, Document, Chunk, CreateLibrary, DocumentCreate, CreateChunk


class LibraryRepository:
    """Thread-safe in-memory repository for managing libraries, documents, and chunks"""
    
    def __init__(self):
        self._lock = threading.RLock()  # Reentrant lock for nested operations
        self._libraries: dict[UUID, Library] = {}
        self._documents: dict[UUID, Document] = {}  # Global document lookup
        self._chunks: dict[UUID, Chunk] = {}        # Global chunk lookup
        
        # Relationship mappings for efficient lookups
        self._library_documents: dict[UUID, set[UUID]] = {}  # library_id -> document_ids
        self._document_chunks: dict[UUID, set[UUID]] = {}    # document_id -> chunk_ids
        self._chunk_document: dict[UUID, UUID] = {}          # chunk_id -> document_id
        self._document_library: dict[UUID, UUID] = {}        # document_id -> library_id
    

    # Library CRUD Operations

    
    def create_library(self, library_data: CreateLibrary) -> Library:
        """Create a new library"""
        with self._lock:
            # Create a new Library object from CreateLibrary data
            library = Library(
                name=library_data.name,
                metadata=library_data.metadata or {},
                documents=[]
            )
            
            if library.id in self._libraries:
                raise ValueError(f"Library with ID {library.id} already exists")
            
            # Store the library
            self._libraries[library.id] = library
            self._library_documents[library.id] = set()
            
            return library
    
    def get_library(self, library_id: UUID) -> Optional[Library]:
        """Get a library by ID with all its documents and chunks"""
        with self._lock:
            library = self._libraries.get(library_id)
            if not library:
                return None
            
            # Build complete library with documents and chunks
            library_copy = deepcopy(library)
            library_copy.documents = self._get_library_documents_internal(library_id)
            
            return library_copy
    
    def get_all_libraries(self) -> List[Library]:
        """Get all libraries with their documents and chunks"""
        with self._lock:
            libraries = []
            for library_id in self._libraries:
                library = self.get_library(library_id)
                if library:
                    libraries.append(library)
            return libraries
    
    def update_library(self, library_id: UUID, **updates) -> Optional[Library]:
        """Update a library's fields"""
        with self._lock:
            library = self._libraries.get(library_id)
            if not library:
                return None
            
            # Update allowed fields
            for field, value in updates.items():
                if hasattr(library, field) and field not in ['id', 'created_at', 'documents']:
                    setattr(library, field, value)
            
            return self.get_library(library_id)
    
    def delete_library(self, library_id: UUID) -> bool:
        """Delete a library and all its documents and chunks"""
        with self._lock:
            if library_id not in self._libraries:
                return False
            
            # Get all documents in the library
            document_ids = self._library_documents.get(library_id, set()).copy()
            
            # Delete all documents (which will delete their chunks)
            for doc_id in document_ids:
                self._delete_document_internal(doc_id)
            
            # Delete the library
            del self._libraries[library_id]
            del self._library_documents[library_id]
            
            return True
    

    # Document CRUD Operations

    
    def create_document(self, document_data: DocumentCreate) -> Optional[Document]:
        """Create a new document in a library"""
        with self._lock:
            if document_data.library_id not in self._libraries:
                return None
            
            # Create a new Document object from DocumentCreate data
            document = Document(
                title=document_data.title,
                metadata=document_data.metadata or {},
                chunks=[],
                library_id=document_data.library_id
            )
            
            if document.id in self._documents:
                raise ValueError(f"Document with ID {document.id} already exists")
            
            # Store the document
            self._documents[document.id] = document
            self._document_chunks[document.id] = set()
            
            # Update relationships
            self._library_documents[document_data.library_id].add(document.id)
            self._document_library[document.id] = document_data.library_id
            
            return document
    
    def get_document(self, document_id: UUID) -> Optional[Document]:
        """Get a document by ID with all its chunks"""
        with self._lock:
            document = self._documents.get(document_id)
            if not document:
                return None
            
            # Build complete document with chunks
            document_copy = deepcopy(document)
            document_copy.chunks = self._get_document_chunks_internal(document_id)
            
            return document_copy
    
    def get_library_documents(self, library_id: UUID) -> List[Document]:
        """Get all documents in a library"""
        with self._lock:
            return self._get_library_documents_internal(library_id)
    
    def update_document(self, document_id: UUID, **updates) -> Optional[Document]:
        """Update a document's fields"""
        with self._lock:
            document = self._documents.get(document_id)
            if not document:
                return None
            
            # Update allowed fields
            for field, value in updates.items():
                if hasattr(document, field) and field not in ['id', 'created_at', 'chunks']:
                    setattr(document, field, value)
            
            return self.get_document(document_id)
    
    def delete_document(self, document_id: UUID) -> bool:
        """Delete a document and all its chunks"""
        with self._lock:
            return self._delete_document_internal(document_id)
    
    def _delete_document_internal(self, document_id: UUID) -> bool:
        """Internal method to delete a document (assumes lock is held)"""
        if document_id not in self._documents:
            return False
        
        # Get all chunks in the document
        chunk_ids = self._document_chunks.get(document_id, set()).copy()
        
        # Delete all chunks
        for chunk_id in chunk_ids:
            self._delete_chunk_internal(chunk_id)
        
        # Remove from library relationship
        library_id = self._document_library.get(document_id)
        if library_id and library_id in self._library_documents:
            self._library_documents[library_id].discard(document_id)
        
        # Delete the document
        del self._documents[document_id]
        del self._document_chunks[document_id]
        if document_id in self._document_library:
            del self._document_library[document_id]
        
        return True
    
    def _get_library_documents_internal(self, library_id: UUID) -> List[Document]:
        """Internal method to get library documents (assumes lock is held)"""
        document_ids = self._library_documents.get(library_id, set())
        documents = []
        
        for doc_id in document_ids:
            document = self.get_document(doc_id)
            if document:
                documents.append(document)
        
        return documents
    

    # Chunk CRUD Operations
    
    def create_chunk(self, chunk: Chunk, document_id: UUID) -> Optional[Chunk]:
        """Create a new chunk in a document"""
        with self._lock:
            if document_id not in self._documents:
                return None
            
            if chunk.id in self._chunks:
                raise ValueError(f"Chunk with ID {chunk.id} already exists")
            
            # Deep copy and store
            chunk_copy = deepcopy(chunk)
            self._chunks[chunk.id] = chunk_copy
            
            # Update relationships
            self._document_chunks[document_id].add(chunk.id)
            self._chunk_document[chunk.id] = document_id
            
            return deepcopy(chunk_copy)
    
    def get_chunk(self, chunk_id: UUID) -> Optional[Chunk]:
        """Get a chunk by ID"""
        with self._lock:
            chunk = self._chunks.get(chunk_id)
            return deepcopy(chunk) if chunk else None
    
    def get_document_chunks(self, document_id: UUID) -> List[Chunk]:
        """Get all chunks in a document"""
        with self._lock:
            return self._get_document_chunks_internal(document_id)
    
    def get_library_chunks(self, library_id: UUID) -> List[Chunk]:
        """Get all chunks in a library (across all documents)"""
        with self._lock:
            chunks = []
            document_ids = self._library_documents.get(library_id, set())
            
            for doc_id in document_ids:
                chunks.extend(self._get_document_chunks_internal(doc_id))
            
            return chunks
    
    def update_chunk(self, chunk_id: UUID, **updates) -> Optional[Chunk]:
        """Update a chunk's fields"""
        with self._lock:
            chunk = self._chunks.get(chunk_id)
            if not chunk:
                return None
            
            # Update allowed fields
            for field, value in updates.items():
                if hasattr(chunk, field) and field not in ['id', 'created_at']:
                    setattr(chunk, field, value)
            
            return self.get_chunk(chunk_id)
    
    def delete_chunk(self, chunk_id: UUID) -> bool:
        """Delete a chunk"""
        with self._lock:
            return self._delete_chunk_internal(chunk_id)
    
    def _delete_chunk_internal(self, chunk_id: UUID) -> bool:
        """Internal method to delete a chunk (assumes lock is held)"""
        if chunk_id not in self._chunks:
            return False
        
        # Remove from document relationship
        document_id = self._chunk_document.get(chunk_id)
        if document_id and document_id in self._document_chunks:
            self._document_chunks[document_id].discard(chunk_id)
        
        # Delete the chunk
        del self._chunks[chunk_id]
        if chunk_id in self._chunk_document:
            del self._chunk_document[chunk_id]
        
        return True
    
    def _get_document_chunks_internal(self, document_id: UUID) -> List[Chunk]:
        """Internal method to get document chunks (assumes lock is held)"""
        chunk_ids = self._document_chunks.get(document_id, set())
        chunks = []
        
        for chunk_id in chunk_ids:
            chunk = self._chunks.get(chunk_id)
            if chunk:
                chunks.append(deepcopy(chunk))
        
        return chunks
    
    # Utility Methods
    
    def get_chunk_document_id(self, chunk_id: UUID) -> Optional[UUID]:
        """Get the document ID that contains a specific chunk"""
        with self._lock:
            return self._chunk_document.get(chunk_id)
    
    def get_document_library_id(self, document_id: UUID) -> Optional[UUID]:
        """Get the library ID that contains a specific document"""
        with self._lock:
            return self._document_library.get(document_id)
    
    def get_chunk_library_id(self, chunk_id: UUID) -> Optional[UUID]:
        """Get the library ID that contains a specific chunk"""
        with self._lock:
            document_id = self._chunk_document.get(chunk_id)
            if document_id:
                return self._document_library.get(document_id)
            return None
    
    def library_exists(self, library_id: UUID) -> bool:
        """Check if a library exists"""
        with self._lock:
            return library_id in self._libraries
    
    def document_exists(self, document_id: UUID) -> bool:
        """Check if a document exists"""
        with self._lock:
            return document_id in self._documents
    
    def chunk_exists(self, chunk_id: UUID) -> bool:
        """Check if a chunk exists"""
        with self._lock:
            return chunk_id in self._chunks
    
    def get_stats(self) -> dict:
        """Get repository statistics"""
        with self._lock:
            return {
                "libraries_count": len(self._libraries),
                "documents_count": len(self._documents),
                "chunks_count": len(self._chunks),
                "total_entities": len(self._libraries) + len(self._documents) + len(self._chunks)
            }
