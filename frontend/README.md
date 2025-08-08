# StackAI Frontend - Modern Testing Interface

A comprehensive, modern React frontend for testing and managing the StackAI Vector Database with backup/rollback capabilities.

## What You'll Find Here

### Core Functionality
- **Library Management**: Create, read, update, and delete vector libraries
- **Document Management**: Manage documents within libraries
- **Chunk Management**: Handle text chunks with embedding support
- **Advanced Search**: Vector similarity search with metadata filtering
- **Index Management**: Build and manage different index types (brute-force, KD-tree)

### Testing & Development Features
- **Settings Backup/Restore**: Create snapshots of your data and roll back changes
- **Bulk Operations**: Import/export data for testing scenarios
- **Testing Tools**: Comprehensive testing utilities and data generators
- **Real-time Health Monitoring**: API status and embedding service monitoring
- **Modern UI**: Clean, responsive interface with excellent UX

### Technical Features
- **TypeScript**: Full type safety and excellent developer experience
- **React Query**: Optimistic updates, caching, and error handling
- **Form Validation**: Zod schema validation with React Hook Form
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Modern Components**: Clean, accessible UI components with Tailwind CSS

## What You Need

- Node.js 18+ and npm/yarn
- StackAI backend running on `http://localhost:8000` (or configure different URL)

## Getting Started

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Environment Configuration (Optional):**
   Create a `.env.local` file to customize the API URL:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Open your browser:**
   Navigate to `http://localhost:3000`

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js 13+ app directory
│   │   ├── globals.css         # Global styles with Tailwind
│   │   ├── layout.tsx          # Root layout with providers
│   │   └── page.tsx            # Main dashboard page
│   ├── components/             # React components
│   │   ├── Header.tsx          # Header with status indicators
│   │   ├── Sidebar.tsx         # Navigation sidebar
│   │   ├── LibraryManager.tsx  # Library CRUD operations
│   │   ├── DocumentManager.tsx # Document management
│   │   ├── ChunkManager.tsx    # Chunk operations
│   │   ├── SearchInterface.tsx # Vector search UI
│   │   ├── IndexManager.tsx    # Index management
│   │   ├── SettingsManager.tsx # Backup/restore settings
│   │   └── TestingTools.tsx    # Testing utilities
│   ├── lib/
│   │   └── api-client.ts       # Comprehensive API client
│   └── types/
│       └── api.ts              # TypeScript type definitions
├── public/                     # Static assets
├── package.json               # Dependencies and scripts
├── tailwind.config.js         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
└── next.config.js             # Next.js configuration
```

## How to Use

### 1. Library Management
- **Create**: Click "Create Library" to add a new library with metadata
- **View**: Browse libraries in an attractive card grid layout
- **Edit**: Click the pencil icon to modify library details
- **Delete**: Click the trash icon to remove a library
- **Navigate**: Click any library card to view its documents

### 2. Document Management
- Select a library first to enable document management
- Create, edit, and delete documents within the selected library
- View document statistics and metadata

### 3. Chunk Management
- Select a document to manage its chunks
- Add chunks with auto-embedding or manual embeddings
- Edit chunk content and metadata
- View embedding status and chunk statistics

### 4. Vector Search
- Select a library to enable search functionality
- Perform text-based searches with auto-embedding
- Use manual embeddings for precise vector searches
- Apply advanced metadata filters
- Configure similarity metrics (cosine, euclidean, dot product)

### 5. Index Management
- Build different index types for optimized search
- Switch between brute-force and KD-tree indexes
- Monitor index status and chunk counts
- Rebuild indexes when needed

### 6. Backup & Restore
- **Create Backups**: Snapshot your current data state
- **View Backups**: Browse backup history with metadata
- **Restore**: Roll back to any previous state
- **Export/Import**: Export data for testing scenarios

### 7. Testing Tools
- Generate sample data for testing
- Bulk import/export operations
- Performance testing utilities
- Data validation tools

## Development

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm start           # Start production server

# Code Quality
npm run lint        # ESLint linting
npm run type-check  # TypeScript type checking

# Testing
npm run test        # Run Vitest tests
npm run test:ui     # Run tests with UI
```

### Key Technologies

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety and developer experience
- **Tailwind CSS**: Utility-first styling framework
- **React Query**: Server state management
- **React Hook Form**: Form handling with validation
- **Zod**: Schema validation
- **Heroicons**: Beautiful icon library
- **React Hot Toast**: Elegant notifications

## UI/UX Features

### Design System
- **Modern Aesthetic**: Clean, professional interface
- **Responsive Layout**: Works on all screen sizes
- **Dark/Light Support**: Automatic theme adaptation
- **Smooth Animations**: Subtle transitions and loading states
- **Accessibility**: WCAG-compliant components

### User Experience
- **Context-Aware Navigation**: Sidebar shows current selection
- **Real-time Feedback**: Toast notifications for all actions
- **Loading States**: Clear indicators for async operations
- **Error Handling**: Graceful error messages with recovery
- **Optimistic Updates**: Immediate UI feedback

### Visual Hierarchy
- **Color-Coded Sections**: Libraries (blue), Documents (green), Chunks (purple)
- **Status Indicators**: Health monitoring and service availability
- **Progress Tracking**: Clear indication of multi-step operations
- **Data Visualization**: Statistics and metadata display

## Backup & Rollback System

### What It Does
- **Automatic Snapshots**: Create timestamped backups
- **Selective Restore**: Choose what to restore
- **Backup Metadata**: Size, counts, and descriptions
- **Local Storage**: Client-side backup storage (can be extended)

### How to Use
1. Navigate to "Settings & Backup"
2. Click "Create Backup" to snapshot current state
3. Provide name and description for the backup
4. View backup history with detailed metadata
5. Click "Restore" on any backup to rollback
6. Optionally export/import backups as JSON files

### Rollback Process
1. **Confirmation**: Clear warning before restore operation
2. **Data Clearing**: Remove current data (configurable)
3. **Progressive Restore**: Libraries → Documents → Chunks
4. **Validation**: Verify restoration success
5. **Notification**: Success/failure feedback

## Testing Features

### Data Generation
- **Sample Libraries**: Pre-configured test libraries
- **Mock Documents**: Various document types and sizes
- **Test Chunks**: Different embedding scenarios
- **Metadata Variations**: Complex metadata structures

### Bulk Operations
- **CSV Import**: Import data from spreadsheets
- **JSON Export**: Export for backup or migration
- **Batch Processing**: Handle large datasets efficiently
- **Progress Tracking**: Monitor bulk operation progress

### Performance Testing
- **Search Benchmarks**: Test search performance
- **Index Comparisons**: Compare index types
- **Load Testing**: Stress test with large datasets
- **Metrics Collection**: Performance statistics

## Production Deployment

### Build for Production
```bash
npm run build
npm start
```

### Environment Variables
```env
NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run linting and type checking
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Troubleshooting

### Common Issues

**API Connection Failed:**
- Ensure StackAI backend is running on the correct port
- Check CORS settings in the backend
- Verify API_BASE_URL environment variable

**Build Errors:**
- Clear node_modules and reinstall dependencies
- Check Node.js version (18+ required)
- Verify TypeScript configuration

**Performance Issues:**
- Use React DevTools Profiler
- Check React Query cache settings
- Optimize component re-renders

### Getting Help

1. Check the browser console for error messages
2. Verify backend API is responding at `/health`
3. Check network tab for failed requests
4. Review backup files for data integrity

## Next Steps

After basic setup, you can:
1. Create your first library and test the interface
2. Import sample data using testing tools
3. Experiment with different search configurations
4. Create backups before making significant changes
5. Explore advanced metadata filtering options 