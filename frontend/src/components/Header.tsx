'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Library, Document } from '@/types/api';
import { 
  WifiIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  CloudIcon,
} from '@heroicons/react/24/outline';

type ActiveTab = 'libraries' | 'documents' | 'chunks' | 'search' | 'indexes' | 'settings' | 'testing';

interface HeaderProps {
  activeTab: ActiveTab;
  selectedLibrary?: Library | null;
  selectedDocument?: Document | null;
}

const tabTitles = {
  libraries: 'Libraries',
  documents: 'Documents',
  chunks: 'Chunks',
  search: 'Vector Search',
  indexes: 'Index Management',
  settings: 'Settings & Backup',
  testing: 'Testing Tools',
};

export default function Header({ activeTab, selectedLibrary, selectedDocument }: HeaderProps) {
  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 30000, // Check every 30 seconds
  });

  const getStatusColor = () => {
    if (healthLoading) return 'text-yellow-500';
    if (health?.status === 'healthy') return 'text-green-500';
    return 'text-red-500';
  };

  const getStatusIcon = () => {
    if (healthLoading) return WifiIcon;
    if (health?.status === 'healthy') return CheckCircleIcon;
    return ExclamationTriangleIcon;
  };

  const StatusIcon = getStatusIcon();

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">
            {tabTitles[activeTab]}
          </h2>
          {selectedLibrary && (
            <div className="flex items-center text-sm text-gray-500 mt-1">
              <span>Library: {selectedLibrary.name}</span>
              {selectedDocument && (
                <span className="ml-4">Document: {selectedDocument.title}</span>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center space-x-4">
          {/* API Status */}
          <div className="flex items-center space-x-2">
            <StatusIcon className={`w-5 h-5 ${getStatusColor()}`} />
            <span className="text-sm font-medium">
              {healthLoading ? 'Checking...' : health?.status === 'healthy' ? 'Connected' : 'Disconnected'}
            </span>
          </div>

          {/* Embedding Service Status */}
          {health?.services?.embedding_service && (
            <div className="flex items-center space-x-2">
              <CloudIcon className={`w-5 h-5 ${
                health.services.embedding_service.available ? 'text-green-500' : 'text-gray-400'
              }`} />
              <span className="text-sm text-gray-600">
                Embeddings: {health.services.embedding_service.available ? 'Available' : 'Unavailable'}
              </span>
            </div>
          )}

          {/* Current Time */}
          <div className="text-sm text-gray-500">
            {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>
    </header>
  );
} 