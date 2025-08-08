'use client';

import { Library } from '@/types/api';

interface IndexManagerProps {
  selectedLibrary: Library | null;
}

export default function IndexManager({ selectedLibrary }: IndexManagerProps) {
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Index Management</h3>
      <p className="text-gray-500">Index management interface will be implemented here</p>
    </div>
  );
} 