'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { apiClient } from '@/lib/api-client';
import { Library, CreateLibrary } from '@/types/api';
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  FolderIcon,
  DocumentTextIcon,
  CubeTransparentIcon,
} from '@heroicons/react/24/outline';

interface LibraryManagerProps {
  onLibrarySelect: (library: Library | null) => void;
}

const createLibrarySchema = z.object({
  name: z.string().min(3, 'Name must be at least 3 characters'),
  metadata: z.string().optional(),
});

type CreateLibraryForm = z.infer<typeof createLibrarySchema>;

export default function LibraryManager({ onLibrarySelect }: LibraryManagerProps) {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingLibrary, setEditingLibrary] = useState<Library | null>(null);
  const queryClient = useQueryClient();

  const { data: libraries, isLoading, error } = useQuery({
    queryKey: ['libraries'],
    queryFn: () => apiClient.getLibraries(),
  });

  const createMutation = useMutation({
    mutationFn: (data: CreateLibrary) => apiClient.createLibrary(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['libraries'] });
      setIsCreateModalOpen(false);
      toast.success('Library created successfully!');
    },
    onError: (error: Error) => {
      toast.error(`Failed to create library: ${error.message}`);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: CreateLibrary }) => 
      apiClient.updateLibrary(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['libraries'] });
      setEditingLibrary(null);
      toast.success('Library updated successfully!');
    },
    onError: (error: Error) => {
      toast.error(`Failed to update library: ${error.message}`);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.deleteLibrary(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['libraries'] });
      toast.success('Library deleted successfully!');
    },
    onError: (error: Error) => {
      toast.error(`Failed to delete library: ${error.message}`);
    },
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateLibraryForm>({
    resolver: zodResolver(createLibrarySchema),
  });

  const onSubmit = (data: CreateLibraryForm) => {
    const libraryData: CreateLibrary = {
      name: data.name,
      metadata: data.metadata ? JSON.parse(data.metadata) : {},
    };

    if (editingLibrary) {
      updateMutation.mutate({ id: editingLibrary.id, data: libraryData });
    } else {
      createMutation.mutate(libraryData);
    }
  };

  const handleEdit = (library: Library) => {
    setEditingLibrary(library);
    reset({
      name: library.name,
      metadata: JSON.stringify(library.metadata, null, 2),
    });
    setIsCreateModalOpen(true);
  };

  const handleDelete = (library: Library) => {
    if (window.confirm(`Are you sure you want to delete "${library.name}"?`)) {
      deleteMutation.mutate(library.id);
    }
  };

  const closeModal = () => {
    setIsCreateModalOpen(false);
    setEditingLibrary(null);
    reset();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
        <span className="ml-2">Loading libraries...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-red-800 font-medium">Error loading libraries</h3>
        <p className="text-red-600 text-sm mt-1">{(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Libraries</h3>
          <p className="text-sm text-gray-500">Manage your document collections</p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="btn-primary flex items-center"
        >
          <PlusIcon className="w-4 h-4 mr-2" />
          Create Library
        </button>
      </div>

      {libraries && libraries.length === 0 ? (
        <div className="text-center py-12">
          <FolderIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No libraries found</h3>
          <p className="text-gray-500 mb-4">Get started by creating your first library</p>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="btn-primary"
          >
            Create Library
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {libraries?.map((library) => (
            <div
              key={library.id}
              className="card-hover cursor-pointer"
              onClick={() => onLibrarySelect(library)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <FolderIcon className="w-8 h-8 text-primary-500 mr-3" />
                  <div>
                    <h4 className="font-medium text-gray-900">{library.name}</h4>
                    <p className="text-sm text-gray-500">
                      {new Date(library.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex space-x-1">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEdit(library);
                    }}
                    className="p-1 text-gray-400 hover:text-gray-600"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(library);
                    }}
                    className="p-1 text-gray-400 hover:text-red-600"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="text-center">
                  <DocumentTextIcon className="w-5 h-5 text-blue-500 mx-auto mb-1" />
                  <span className="block font-medium">{library.documents.length}</span>
                  <span className="text-gray-500">Documents</span>
                </div>
                <div className="text-center">
                  <CubeTransparentIcon className="w-5 h-5 text-green-500 mx-auto mb-1" />
                  <span className="block font-medium">
                    {library.documents.reduce((acc, doc) => acc + doc.chunks.length, 0)}
                  </span>
                  <span className="text-gray-500">Chunks</span>
                </div>
                <div className="text-center">
                  <div className="w-5 h-5 bg-purple-500 rounded mx-auto mb-1"></div>
                  <span className="block font-medium">
                    {Object.keys(library.metadata).length}
                  </span>
                  <span className="text-gray-500">Metadata</span>
                </div>
              </div>

              {Object.keys(library.metadata).length > 0 && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Metadata:</p>
                  <pre className="text-xs text-gray-700 overflow-x-auto">
                    {JSON.stringify(library.metadata, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              {editingLibrary ? 'Edit Library' : 'Create Library'}
            </h3>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name
                </label>
                <input
                  {...register('name')}
                  className="input"
                  placeholder="Enter library name"
                />
                {errors.name && (
                  <p className="text-red-600 text-sm mt-1">{errors.name.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Metadata (JSON)
                </label>
                <textarea
                  {...register('metadata')}
                  className="input h-32 font-mono text-sm"
                  placeholder='{"key": "value"}'
                />
                {errors.metadata && (
                  <p className="text-red-600 text-sm mt-1">{errors.metadata.message}</p>
                )}
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  disabled={createMutation.isPending || updateMutation.isPending}
                  className="btn-primary flex-1"
                >
                  {createMutation.isPending || updateMutation.isPending ? (
                    <>
                      <div className="spinner mr-2"></div>
                      {editingLibrary ? 'Updating...' : 'Creating...'}
                    </>
                  ) : (
                    editingLibrary ? 'Update Library' : 'Create Library'
                  )}
                </button>
                <button
                  type="button"
                  onClick={closeModal}
                  className="btn-outline flex-1"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
} 