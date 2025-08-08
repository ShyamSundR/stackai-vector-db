// Base types
export interface Metadata {
  [key: string]: any;
}

// Library types
export interface CreateLibrary {
  name: string;
  metadata?: Metadata;
}

export interface UpdateLibrary {
  name?: string;
  metadata?: Metadata;
}

export interface Library {
  id: string;
  name: string;
  documents: Document[];
  metadata: Metadata;
  created_at: string;
}

// Document types
export interface CreateDocument {
  title: string;
  library_id: string;
  metadata?: Metadata;
}

export interface UpdateDocument {
  title?: string;
  metadata?: Metadata;
}

export interface Document {
  id: string;
  title: string;
  library_id: string;
  chunks: Chunk[];
  metadata: Metadata;
  created_at: string;
}

// Chunk types
export interface CreateChunk {
  text: string;
  embedding?: number[];
  auto_embed?: boolean;
  metadata?: Metadata;
}

export interface UpdateChunk {
  text?: string;
  embedding?: number[];
  metadata?: Metadata;
}

export interface Chunk {
  id: string;
  text: string;
  document_id: string;
  embedding?: number[];
  metadata: Metadata;
  created_at: string;
}

// Search types
export interface SearchRequest {
  query_embedding?: number[];
  query_text?: string;
  k?: number;
  similarity_metric?: 'cosine' | 'euclidean' | 'dot_product';
  metadata_filter?: MetadataFilter;
}

export interface MetadataFilter {
  [key: string]: FilterCondition | any;
}

export interface FilterCondition {
  $eq?: any;
  $ne?: any;
  $gt?: any;
  $gte?: any;
  $lt?: any;
  $lte?: any;
  $in?: any[];
  $nin?: any[];
  $contains?: string;
  $regex?: string;
  $exists?: boolean;
  $date_after?: string;
  $date_before?: string;
  $date_range?: [string, string];
}

export interface SearchResultItem {
  chunk: Chunk;
  distance: number;
  similarity: number;
}

// Index types
export interface IndexInfo {
  library_id: string;
  index_type: string | null;
  chunk_count: number;
  indexed: boolean;
}

export interface BuildIndexResponse {
  message: string;
  library_id: string;
  index_type: string;
  chunks_indexed: number;
}

// Health check
export interface HealthResponse {
  status: string;
  app: string;
  version: string;
  services: {
    embedding_service: {
      available: boolean;
      cohere_configured: boolean;
      model: string | null;
    };
  };
}

// API Error
export interface ApiError {
  detail: string;
}

// Settings backup/restore types
export interface SettingsBackup {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  data: {
    libraries: Library[];
    // Add other settings as needed
  };
}

export interface BackupMetadata {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  size: number;
  library_count: number;
  document_count: number;
  chunk_count: number;
} 