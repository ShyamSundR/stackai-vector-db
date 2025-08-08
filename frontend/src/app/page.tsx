'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image'
import { 
  FolderIcon, 
  DocumentTextIcon, 
  CubeTransparentIcon,
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  CogIcon,
  BeakerIcon,
  TrashIcon,
  PlusIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

// Add import for HierarchyExplainer
import HierarchyExplainer from '@/components/HierarchyExplainer';

interface Library {
  id: string;
  name: string;
  metadata: any;
  created_at: string;
  documents: any[];
}

interface Document {
  id: string;
  title: string;
  library_id: string;
  metadata?: Record<string, any>;
  created_at: string;
  chunks?: any[];
}

type ActiveView = 'libraries' | 'documents' | 'chunks' | 'search' | 'indexes' | 'settings' | 'testing';

export default function Dashboard() {
  const [activeView, setActiveView] = useState<ActiveView>('libraries');
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [selectedLibrary, setSelectedLibrary] = useState<Library | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newLibraryName, setNewLibraryName] = useState('');
  const [backendStatus, setBackendStatus] = useState<string>('Checking...');

  // Add debug flag
  const [debugMode, setDebugMode] = useState(false);

  // Document creation interface
  const [showDocumentForm, setShowDocumentForm] = useState(false);
  const [newDocumentTitle, setNewDocumentTitle] = useState('');
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  // Chunks state
  const [chunks, setChunks] = useState<any[]>([]);
  const [showChunkForm, setShowChunkForm] = useState(false);
  const [newChunkText, setNewChunkText] = useState('');
  const [autoEmbed, setAutoEmbed] = useState(true);
  const [chunkMetadata, setChunkMetadata] = useState('');
  // Search state
  const [queryText, setQueryText] = useState('');
  const [queryEmbedding, setQueryEmbedding] = useState(''); // JSON array string
  const [topK, setTopK] = useState(5);
  const [similarityMetric, setSimilarityMetric] = useState<'cosine' | 'euclidean' | 'dot_product'>('cosine');
  const [metadataFilter, setMetadataFilter] = useState(''); // JSON
  const [searchResults, setSearchResults] = useState<any[]>([]);

  // Navigation items
  const navItems = [
    { id: 'libraries', name: 'Libraries', icon: FolderIcon },
    { id: 'documents', name: 'Documents', icon: DocumentTextIcon, requiresLibrary: true },
    { id: 'chunks', name: 'Chunks', icon: CubeTransparentIcon, requiresLibrary: true },
    { id: 'search', name: 'Vector Search', icon: MagnifyingGlassIcon, requiresLibrary: true },
    { id: 'indexes', name: 'Index Management', icon: AdjustmentsHorizontalIcon, requiresLibrary: true },
    { id: 'settings', name: 'Settings & Backup', icon: CogIcon },
    { id: 'testing', name: 'Testing Tools', icon: BeakerIcon },
  ];

  // Modify useEffect to handle errors better
  useEffect(() => {
    const initializeApp = async () => {
      const isConnected = await checkBackendConnection();
      if (isConnected) {
        await loadLibraries();
      }
    };
    
    initializeApp();
  }, []);

  // Load chunks whenever selectedDocument changes or view switches to chunks
  useEffect(() => {
    if (activeView === 'chunks' && selectedDocument) {
      void loadChunks(selectedDocument.id);
    }
  }, [activeView, selectedDocument]);

  const checkBackendConnection = async () => {
    try {
      console.log('Checking backend connection...');
      const response = await fetch('http://localhost:8000/health');
      console.log('Health check response status:', response.status);
      
      const data = await response.json();
      console.log('Health check data:', data);
      
      setBackendStatus(`✅ ${data.app} - ${data.status}`);
      
      // Test libraries endpoint
      const librariesResponse = await fetch('http://localhost:8000/api/v1/libraries/');
      console.log('Libraries endpoint response:', librariesResponse.status);
      if (!librariesResponse.ok) {
        throw new Error('Libraries endpoint not responding');
      }
      
      return true;
    } catch (error: any) {
      console.error('Backend connection error:', error);
      setBackendStatus('❌ Backend not connected');
      setError(`Cannot connect to backend: ${error.message}. Make sure it's running on port 8000.`);
      return false;
    }
  };

  const loadLibraries = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    setError(null);
    try {
      console.log('Loading libraries...');
      const response = await fetch('http://localhost:8000/api/v1/libraries/');
      console.log('Libraries response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Libraries data:', data);
      
      setLibraries(data);
    } catch (error: any) {
      console.error('Error loading libraries:', error);
      setError(`Failed to load libraries: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const loadChunks = async (documentId: string) => {
    try {
      setIsLoading(true);
      const res = await fetch(`http://localhost:8000/api/v1/chunks/document/${documentId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setChunks(data);
    } catch (e: any) {
      setError(`Failed to load chunks: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const createLibrary = async () => {
    if (!newLibraryName.trim()) {
      setError('Library name cannot be empty');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Creating library:', { name: newLibraryName });
      
      const response = await fetch('http://localhost:8000/api/v1/libraries/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          name: newLibraryName,
          metadata: { created_via: 'frontend', environment: 'test' }
        }),
      });
      
      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);
      
      if (!response.ok) {
        throw new Error(data.detail || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      setLibraries([...libraries, data]);
      setNewLibraryName('');
      setShowCreateForm(false);
      
      // Show success message
      const successDiv = document.createElement('div');
      successDiv.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg';
      successDiv.textContent = 'Library created successfully!';
      document.body.appendChild(successDiv);
      setTimeout(() => successDiv.remove(), 3000);
      
    } catch (error: any) {
      console.error('Error creating library:', error);
      setError(`Failed to create library: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteLibrary = async (libraryId: string, libraryName: string) => {
    if (!confirm(`Are you sure you want to delete "${libraryName}"?`)) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/libraries/${libraryId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      setLibraries(libraries.filter(lib => lib.id !== libraryId));
      if (selectedLibrary?.id === libraryId) {
        setSelectedLibrary(null);
        setActiveView('libraries');
      }
    } catch (error) {
      setError(`Failed to delete library: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Update the createDocument function to match the backend API
  const createDocument = async () => {
    if (!newDocumentTitle.trim() || !selectedLibrary) {
      setError('Document title cannot be empty and library must be selected');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      console.log('Creating document:', { 
        title: newDocumentTitle, 
        library_id: selectedLibrary.id 
      });

      const response = await fetch('http://localhost:8000/api/v1/documents/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          title: newDocumentTitle,
          library_id: selectedLibrary.id,
          metadata: { created_via: 'frontend', environment: 'test' }
        }),
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);

      if (!response.ok) {
        throw new Error(data.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      // Update the selected library's documents
      setSelectedLibrary(prev => {
        if (!prev) return null;
        return {
          ...prev,
          documents: [...prev.documents, data]
        };
      });

      // Also update the library in the libraries list
      setLibraries(prevLibs => 
        prevLibs.map(lib => 
          lib.id === selectedLibrary.id 
            ? { ...lib, documents: [...lib.documents, data] }
            : lib
        )
      );

      setNewDocumentTitle('');
      setShowDocumentForm(false);

      // Show success message
      const successDiv = document.createElement('div');
      successDiv.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg';
      successDiv.textContent = 'Document created successfully!';
      document.body.appendChild(successDiv);
      setTimeout(() => successDiv.remove(), 3000);

    } catch (error: any) {
      console.error('Error creating document:', error);
      setError(`Failed to create document: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteDocument = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/libraries/${selectedLibrary?.id}/documents/${documentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      setSelectedLibrary(prev => prev ? { ...prev, documents: prev.documents.filter(doc => doc.id !== documentId) } : null);
      setSelectedDocument(null);
      setActiveView('documents');

    } catch (error) {
      setError(`Failed to delete document: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const createChunk = async () => {
    if (!selectedDocument) { setError('Select a document'); return; }
    if (!newChunkText.trim()) { setError('Chunk text cannot be empty'); return; }
    setIsLoading(true);
    setError(null);
    try {
      const body: any = { text: newChunkText };
      if (!autoEmbed) body.embedding = []; // optional manual embedding placeholder
      if (chunkMetadata.trim()) {
        try { body.metadata = JSON.parse(chunkMetadata); } catch { throw new Error('Invalid chunk metadata JSON'); }
      }
      const url = `http://localhost:8000/api/v1/chunks/?document_id=${selectedDocument.id}`;
      const res = await fetch(url, { method:'POST', headers:{ 'Content-Type':'application/json' }, body: JSON.stringify(body) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
      setChunks(prev => [data, ...prev]);
      setShowChunkForm(false); setNewChunkText(''); setChunkMetadata('');
    } catch (e:any) {
      setError(`Failed to create chunk: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteChunk = async (chunkId: string) => {
    if (!confirm('Delete this chunk?')) return;
    setIsLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/chunks/${chunkId}`, { method: 'DELETE' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setChunks(prev => prev.filter(c => c.id !== chunkId));
    } catch (e:any) {
      setError(`Failed to delete chunk: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const runSearch = async () => {
    if (!selectedLibrary) { setError('Select a library'); return; }
    setIsLoading(true); setError(null); setSearchResults([]);
    try {
      const body:any = { k: topK, similarity_metric: similarityMetric };
      if (queryText.trim()) body.query_text = queryText.trim();
      if (queryEmbedding.trim()) {
        try { body.query_embedding = JSON.parse(queryEmbedding); } catch { throw new Error('Invalid embedding JSON'); }
      }
      if (!body.query_text && !body.query_embedding) {
        throw new Error('Provide query text or query embedding');
      }
      if (metadataFilter.trim()) {
        try { body.metadata_filter = JSON.parse(metadataFilter); } catch { throw new Error('Invalid metadata filter JSON'); }
      }
      const res = await fetch(`http://localhost:8000/api/v1/search/libraries/${selectedLibrary.id}/search`, {
        method:'POST', headers:{ 'Content-Type':'application/json' }, body: JSON.stringify(body)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
      setSearchResults(data);
    } catch (e:any) {
      setError(`Search failed: ${e.message}`);
    } finally { setIsLoading(false); }
  };

  const renderContent = () => {
    switch (activeView) {
      case 'libraries':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">
                Libraries ({libraries.length})
              </h2>
              <button
                onClick={() => setShowCreateForm(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
              >
                <PlusIcon className="w-5 h-5 mr-2" />
                Create Library
              </button>
            </div>

            {/* Add Hierarchy Explainer */}
            {libraries.length === 0 && <HierarchyExplainer />}

            {libraries.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg border-2 border-dashed border-gray-300">
                <FolderIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-sm font-medium text-gray-900">No libraries</h3>
                <p className="text-sm text-gray-500 mt-1">Get started by creating a new library.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {libraries.map((library) => (
                  <div
                    key={library.id}
                    onClick={() => {
                      setSelectedLibrary(library);
                      setActiveView('documents');
                    }}
                    className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center">
                        <FolderIcon className="w-8 h-8 text-blue-500 mr-3" />
                        <div>
                          <h3 className="font-medium text-gray-900">{library.name}</h3>
                          <p className="text-sm text-gray-500">
                            {new Date(library.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteLibrary(library.id, library.name);
                        }}
                        className="text-gray-400 hover:text-red-600"
                      >
                        <TrashIcon className="w-5 h-5" />
                      </button>
                    </div>

                    <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                      <div className="flex items-center">
                        <DocumentTextIcon className="w-5 h-5 text-gray-400 mr-2" />
                        <span>{library.documents.length} documents</span>
                      </div>
                      <div className="flex items-center">
                        <CubeTransparentIcon className="w-5 h-5 text-gray-400 mr-2" />
                        <span>
                          {library.documents.reduce((acc, doc) => acc + (doc.chunks?.length || 0), 0)} chunks
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 'documents':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">
                {selectedLibrary ? `Documents in ${selectedLibrary.name}` : 'Select a Library'}
              </h2>
              {selectedLibrary && (
                <button
                  onClick={() => setShowDocumentForm(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
                >
                  <PlusIcon className="w-5 h-5 mr-2" />
                  Add Document
                </button>
              )}
            </div>

            {selectedLibrary?.documents.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg border-2 border-dashed border-gray-300">
                <DocumentTextIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-sm font-medium text-gray-900">No documents</h3>
                <p className="text-sm text-gray-500 mt-1">Add your first document to this library.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {selectedLibrary?.documents.map((doc) => (
                  <div
                    key={doc.id}
                    onClick={() => {
                      setSelectedDocument(doc);
                      setActiveView('chunks');
                    }}
                    className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-medium text-gray-900">{doc.title}</h3>
                        <p className="text-sm text-gray-500">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteDocument(doc.id);
                        }}
                        className="text-gray-400 hover:text-red-600"
                      >
                        <TrashIcon className="w-5 h-5" />
                      </button>
                    </div>

                    <div className="mt-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <CubeTransparentIcon className="w-5 h-5 text-gray-400 mr-2" />
                        <span>{doc.chunks?.length || 0} chunks</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Document Creation Modal */}
            {showDocumentForm && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium text-gray-900">Create New Document</h3>
                    <button
                      onClick={() => setShowDocumentForm(false)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <XMarkIcon className="w-5 h-5" />
                    </button>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Document Title
                      </label>
                      <input
                        type="text"
                        value={newDocumentTitle}
                        onChange={(e) => setNewDocumentTitle(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                        placeholder="Enter document title"
                        autoFocus
                      />
                    </div>

                    <div className="flex space-x-3 pt-4">
                      <button
                        onClick={createDocument}
                        disabled={isLoading || !newDocumentTitle.trim()}
                        className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                      >
                        {isLoading ? (
                          <span className="flex items-center justify-center">
                            <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                            Creating...
                          </span>
                        ) : (
                          'Create Document'
                        )}
                      </button>
                      <button
                        onClick={() => {
                          setShowDocumentForm(false);
                          setNewDocumentTitle('');
                        }}
                        className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        );

      case 'chunks':
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">Chunks {selectedDocument ? `for ${selectedDocument.title}` : ''}</h2>
              {selectedDocument && (
                <button onClick={()=>setShowChunkForm(true)} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center">
                  <PlusIcon className="w-5 h-5 mr-2" /> Add Chunk
                </button>
              )}
            </div>
            {!selectedDocument && <p className="text-gray-500">Select a document in Documents view first.</p>}
            {selectedDocument && (
              <>
                {isLoading && <p className="text-gray-500">Loading...</p>}
                {!isLoading && chunks.length === 0 && (
                  <div className="text-center py-12 bg-white rounded-lg border-2 border-dashed border-gray-300">
                    <CubeTransparentIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-sm font-medium text-gray-900">No chunks</h3>
                    <p className="text-sm text-gray-500 mt-1">Add your first chunk.</p>
                  </div>
                )}
                <div className="space-y-3">
                  {chunks.map((chunk)=> (
                    <div key={chunk.id} className="bg-white rounded-lg border border-gray-200 p-4">
                      <div className="flex justify-between items-start">
                        <pre className="text-sm text-gray-900 whitespace-pre-wrap">{chunk.text}</pre>
                        <button onClick={()=>deleteChunk(chunk.id)} className="text-gray-400 hover:text-red-600"><TrashIcon className="w-5 h-5"/></button>
                      </div>
                      <div className="mt-2 text-xs text-gray-500">{new Date(chunk.created_at).toLocaleString()}</div>
                      {chunk.metadata && Object.keys(chunk.metadata).length>0 && (
                        <pre className="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded">{JSON.stringify(chunk.metadata, null, 2)}</pre>
                      )}
                    </div>
                  ))}
                </div>
              </>
            )}
            {showChunkForm && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg shadow-xl w-full max-w-lg p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-medium text-gray-900">Create Chunk</h3>
                    <button onClick={()=>setShowChunkForm(false)} className="text-gray-400 hover:text-gray-600"><XMarkIcon className="w-5 h-5"/></button>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Text</label>
                      <textarea value={newChunkText} onChange={(e)=>setNewChunkText(e.target.value)} className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900" placeholder="Paste chunk text"></textarea>
                    </div>
                    <div className="flex items-center space-x-3">
                      <input id="autoEmbed" type="checkbox" checked={autoEmbed} onChange={(e)=>setAutoEmbed(e.target.checked)} />
                      <label htmlFor="autoEmbed" className="text-sm text-gray-700">Auto-generate embedding (if embedding service is configured)</label>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Metadata (JSON)</label>
                      <textarea value={chunkMetadata} onChange={(e)=>setChunkMetadata(e.target.value)} className="w-full h-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900" placeholder='{"section":"intro","page":1}'></textarea>
                    </div>
                    <div className="flex space-x-3 pt-2">
                      <button onClick={createChunk} disabled={isLoading || !newChunkText.trim()} className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">{isLoading? 'Creating...' : 'Create Chunk'}</button>
                      <button onClick={()=>{setShowChunkForm(false); setNewChunkText(''); setChunkMetadata('');}} className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200">Cancel</button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        );

      case 'search':
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Vector Search {selectedLibrary ? `in ${selectedLibrary.name}` : ''}</h2>
            {!selectedLibrary && <p className="text-gray-500">Select a library first.</p>}
            {selectedLibrary && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1 bg-white border border-gray-200 rounded-lg p-6">
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Query Text</label>
                      <textarea value={queryText} onChange={(e)=>setQueryText(e.target.value)} className="w-full h-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900" placeholder="Enter natural language query"></textarea>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Query Embedding (JSON array)</label>
                      <textarea value={queryEmbedding} onChange={(e)=>setQueryEmbedding(e.target.value)} className="w-full h-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900" placeholder="[0.1, 0.2, ...]"></textarea>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Top K</label>
                        <input type="number" min={1} value={topK} onChange={(e)=>setTopK(parseInt(e.target.value||'1'))} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Metric</label>
                        <select value={similarityMetric} onChange={(e)=>setSimilarityMetric(e.target.value as any)} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900">
                          <option value="cosine">cosine</option>
                          <option value="euclidean">euclidean</option>
                          <option value="dot_product">dot_product</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Metadata Filter (JSON)</label>
                      <textarea value={metadataFilter} onChange={(e)=>setMetadataFilter(e.target.value)} className="w-full h-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900" placeholder='{"year":{"$gte":2020}}'></textarea>
                    </div>
                    <button onClick={runSearch} className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">Run Search</button>
                  </div>
                </div>
                <div className="lg:col-span-2">
                  {isLoading && <p className="text-gray-500">Searching...</p>}
                  {!isLoading && searchResults.length === 0 && <p className="text-gray-500">No results yet.</p>}
                  <div className="space-y-3">
                    {searchResults.map((r:any, idx:number)=> (
                      <div key={idx} className="bg-white border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between text-sm text-gray-600">
                          <div>Similarity: <span className="font-medium text-gray-900">{r.similarity?.toFixed?.(3)}</span></div>
                          <div>Distance: <span className="text-gray-900">{r.distance?.toFixed?.(3)}</span></div>
                        </div>
                        <pre className="mt-2 text-sm text-gray-900 whitespace-pre-wrap">{r.chunk?.text}</pre>
                        {r.chunk?.metadata && Object.keys(r.chunk.metadata).length>0 && (
                          <pre className="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded">{JSON.stringify(r.chunk.metadata, null, 2)}</pre>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        );

      case 'indexes':
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Index Management</h2>
            <p className="text-gray-500">Index management will be implemented here.</p>
          </div>
        );

      case 'settings':
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Settings & Backup</h2>
            <p className="text-gray-500">Settings and backup features will be implemented here.</p>
          </div>
        );

      case 'testing':
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Testing Tools</h2>
            <p className="text-gray-500">Testing utilities will be implemented here.</p>
          </div>
        );

      default:
        return null;
    }
  };

  // Add debug output in the UI
  const renderDebugInfo = () => {
    if (!debugMode) return null;

    return (
      <div className="fixed bottom-4 left-4 bg-gray-900 text-white p-4 rounded-lg shadow-lg max-w-lg opacity-90">
        <h4 className="font-mono text-sm mb-2">Debug Info:</h4>
        <pre className="text-xs overflow-auto">
          {JSON.stringify({
            backendStatus,
            libraryCount: libraries.length,
            error,
            isLoading,
            showCreateForm,
            showDocumentForm,
            newDocumentTitle,
            selectedDocument,
          }, null, 2)}
        </pre>
      </div>
    );
  };

  // Add debug toggle in the header
  const renderDebugToggle = () => (
    <button
      onClick={() => setDebugMode(!debugMode)}
      className="text-xs text-gray-500 hover:text-gray-700"
    >
      {debugMode ? 'Hide Debug' : 'Show Debug'}
    </button>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200">
        <div className="p-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Image src="/stackai-mark.svg" alt="StackAI" width={22} height={22} priority className="rounded-md ring-1 ring-gray-200" />
              <h1 className="text-xl font-bold text-gray-900">StackAI</h1>
            </div>
            {renderDebugToggle()}
          </div>
          <p className="text-sm text-gray-500 mt-1">{backendStatus}</p>
        </div>

        <nav className="px-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isDisabled = item.requiresLibrary && !selectedLibrary;
            const isActive = activeView === item.id;

            return (
              <button
                key={item.id}
                onClick={() => !isDisabled && setActiveView(item.id as ActiveView)}
                disabled={isDisabled}
                className={`
                  w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg
                  ${isActive ? 'bg-blue-50 text-blue-700' : ''}
                  ${isDisabled ? 'text-gray-400 cursor-not-allowed' : 'text-gray-700 hover:bg-gray-50'}
                `}
              >
                <Icon className="w-5 h-5 mr-3" />
                {item.name}
                {isDisabled && (
                  <span className="ml-auto text-xs text-gray-400">
                    Select library
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {selectedLibrary && (
          <div className="mt-8 px-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-700">Selected Library</h3>
              <p className="text-sm text-gray-500 mt-1">{selectedLibrary.name}</p>
              <button
                onClick={() => {
                  setSelectedLibrary(null);
                  setActiveView('libraries');
                }}
                className="mt-2 text-xs text-blue-600 hover:text-blue-700"
              >
                Clear Selection
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="py-8 px-8">
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <XMarkIcon className="h-5 w-5 text-red-400" />
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
                <div className="ml-auto">
                  <button
                    onClick={() => setError(null)}
                    className="text-red-400 hover:text-red-600"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          )}

          {renderContent()}
        </div>
      </div>

      {/* Create Library Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Create New Library</h3>
              <button
                onClick={() => setShowCreateForm(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Library Name
                </label>
                <input
                  type="text"
                  value={newLibraryName}
                  onChange={(e) => setNewLibraryName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                  placeholder="Enter library name"
                  autoFocus
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  onClick={createLibrary}
                  disabled={isLoading || !newLibraryName.trim()}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Creating...
                    </span>
                  ) : (
                    'Create Library'
                  )}
                </button>
                <button
                  onClick={() => {
                    setShowCreateForm(false);
                    setNewLibraryName('');
                  }}
                  className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {renderDebugInfo()}
    </div>
  );
} 