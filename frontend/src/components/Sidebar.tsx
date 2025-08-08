'use client';

import { Library, Document } from '@/types/api';
import {
  FolderIcon,
  DocumentTextIcon,
  CubeTransparentIcon,
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  CogIcon,
  BeakerIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';

type ActiveTab = 'libraries' | 'documents' | 'chunks' | 'search' | 'indexes' | 'settings' | 'testing';

interface SidebarProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  selectedLibrary?: Library | null;
  selectedDocument?: Document | null;
}

const navigationItems = [
  { id: 'libraries', name: 'Libraries', icon: FolderIcon },
  { id: 'documents', name: 'Documents', icon: DocumentTextIcon },
  { id: 'chunks', name: 'Chunks', icon: CubeTransparentIcon },
  { id: 'search', name: 'Search', icon: MagnifyingGlassIcon },
  { id: 'indexes', name: 'Indexes', icon: AdjustmentsHorizontalIcon },
  { id: 'settings', name: 'Settings', icon: CogIcon },
  { id: 'testing', name: 'Testing', icon: BeakerIcon },
] as const;

export default function Sidebar({
  activeTab,
  onTabChange,
  selectedLibrary,
  selectedDocument,
}: SidebarProps) {
  return (
    <div className="w-64 bg-white shadow-sm border-r border-gray-200 flex flex-col">
      <div className="p-6">
        <h1 className="text-xl font-semibold text-gray-900">StackAI</h1>
        <p className="text-sm text-gray-500 mt-1">Vector Database Testing</p>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          const isDisabled = 
            (item.id === 'documents' && !selectedLibrary) ||
            (item.id === 'chunks' && !selectedDocument) ||
            (item.id === 'search' && !selectedLibrary) ||
            (item.id === 'indexes' && !selectedLibrary);

          return (
            <button
              key={item.id}
              onClick={() => !isDisabled && onTabChange(item.id as ActiveTab)}
              disabled={isDisabled}
              className={clsx(
                'w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                isActive
                  ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-500'
                  : isDisabled
                  ? 'text-gray-400 cursor-not-allowed'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              <Icon className="w-5 h-5 mr-3" />
              {item.name}
              {isDisabled && (
                <span className="ml-auto text-xs text-gray-400">
                  {item.id === 'documents' && '(Select library)'}
                  {item.id === 'chunks' && '(Select document)'}
                  {(item.id === 'search' || item.id === 'indexes') && '(Select library)'}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {selectedLibrary && (
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
            Current Context
          </div>
          <div className="space-y-2">
            <div className="flex items-center text-sm">
              <FolderIcon className="w-4 h-4 text-primary-500 mr-2" />
              <span className="truncate font-medium">{selectedLibrary.name}</span>
            </div>
            {selectedDocument && (
              <div className="flex items-center text-sm ml-6">
                <ChevronRightIcon className="w-3 h-3 text-gray-400 mr-1" />
                <DocumentTextIcon className="w-4 h-4 text-blue-500 mr-2" />
                <span className="truncate">{selectedDocument.title}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
} 