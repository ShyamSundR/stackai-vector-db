'use client';

import { Library } from '@/types/api';

interface SearchInterfaceProps {
  selectedLibrary: Library | null;
}

export default function SearchInterface({ selectedLibrary }: SearchInterfaceProps) {
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Vector Search</h3>
      <p className="text-gray-500">Advanced search interface will be implemented here</p>
    </div>
  );
} 