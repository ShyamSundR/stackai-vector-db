'use client';

import { Library, Document } from '@/types/api';

interface ChunkManagerProps {
  selectedLibrary: Library | null;
  selectedDocument: Document | null;
}

export default function ChunkManager({ selectedLibrary, selectedDocument }: ChunkManagerProps) {
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Chunk Management</h3>
      <p className="text-gray-500">Chunk management interface will be implemented here</p>
    </div>
  );
} 