'use client';

import { Library, Document } from '@/types/api';

interface DocumentManagerProps {
  selectedLibrary: Library | null;
  onDocumentSelect: (document: Document | null) => void;
}

export default function DocumentManager({ selectedLibrary, onDocumentSelect }: DocumentManagerProps) {
  if (!selectedLibrary) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Please select a library to manage documents</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">
        Documents in {selectedLibrary.name}
      </h3>
      <p className="text-gray-500">Document management interface will be implemented here</p>
    </div>
  );
} 