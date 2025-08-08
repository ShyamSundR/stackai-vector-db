'use client';

import { FolderIcon, DocumentTextIcon, CubeTransparentIcon } from '@heroicons/react/24/outline';

export default function HierarchyExplainer() {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">StackAI Structure</h3>
      
      <div className="space-y-6">
        {/* Library Level */}
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
            <FolderIcon className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-900">Libraries</h4>
            <p className="text-sm text-gray-500">Top-level containers for your documents</p>
            <p className="text-xs text-gray-400 mt-1">Example: "Research Papers", "Technical Documentation"</p>
          </div>
        </div>

        {/* Arrow */}
        <div className="ml-4 border-l-2 border-dashed border-gray-300 pl-8 relative">
          <div className="absolute -left-2 top-1/2 w-4 h-4 border-b-2 border-l-2 border-dashed border-gray-300"></div>
        </div>

        {/* Document Level */}
        <div className="flex items-start space-x-4 ml-8">
          <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
            <DocumentTextIcon className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-900">Documents</h4>
            <p className="text-sm text-gray-500">Individual files or texts within libraries</p>
            <p className="text-xs text-gray-400 mt-1">Example: "Introduction to AI.pdf", "System Architecture.md"</p>
          </div>
        </div>

        {/* Arrow */}
        <div className="ml-12 border-l-2 border-dashed border-gray-300 pl-8 relative">
          <div className="absolute -left-2 top-1/2 w-4 h-4 border-b-2 border-l-2 border-dashed border-gray-300"></div>
        </div>

        {/* Chunk Level */}
        <div className="flex items-start space-x-4 ml-16">
          <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
            <CubeTransparentIcon className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h4 className="text-sm font-medium text-gray-900">Chunks</h4>
            <p className="text-sm text-gray-500">Small sections of text from documents with embeddings</p>
            <p className="text-xs text-gray-400 mt-1">Example: Paragraphs or sections with vector embeddings</p>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">How it works:</h4>
        <ol className="text-sm text-gray-600 space-y-2 list-decimal list-inside">
          <li>Create a library to organize your content</li>
          <li>Add documents to your library</li>
          <li>Documents are automatically split into chunks</li>
          <li>Chunks get vector embeddings for similarity search</li>
        </ol>
      </div>
    </div>
  );
} 