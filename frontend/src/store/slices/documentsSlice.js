import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import documentService from '@/services/documentService';

// Async thunks
export const fetchDocuments = createAsyncThunk(
  'documents/fetchAll',
  async (params, { rejectWithValue }) => {
    try {
      const response = await documentService.getDocuments(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch documents');
    }
  }
);

export const fetchDocumentById = createAsyncThunk(
  'documents/fetchById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await documentService.getDocumentById(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch document');
    }
  }
);

export const uploadDocument = createAsyncThunk(
  'documents/upload',
  async ({ file, onProgress }, { rejectWithValue }) => {
    try {
      const response = await documentService.uploadDocument(file, onProgress);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to upload document');
    }
  }
);

export const deleteDocument = createAsyncThunk(
  'documents/delete',
  async (id, { rejectWithValue }) => {
    try {
      await documentService.deleteDocument(id);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete document');
    }
  }
);

export const extractDocumentData = createAsyncThunk(
  'documents/extract',
  async (id, { rejectWithValue }) => {
    try {
      const response = await documentService.extractData(id);
      return { id, data: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to extract data');
    }
  }
);

export const searchDocuments = createAsyncThunk(
  'documents/search',
  async (query, { rejectWithValue }) => {
    try {
      const response = await documentService.searchDocuments(query);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to search documents');
    }
  }
);

export const downloadDocument = createAsyncThunk(
  'documents/download',
  async (id, { rejectWithValue }) => {
    try {
      const response = await documentService.downloadDocument(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to download document');
    }
  }
);

// Initial state
const initialState = {
  documents: [],
  currentDocument: null,
  searchResults: [],
  uploadProgress: {},
  loading: false,
  error: null,
  pagination: {
    page: 1,
    pageSize: 10,
    total: 0,
    totalPages: 0,
  },
  filters: {
    search: '',
    type: '',
    dateFrom: '',
    dateTo: '',
  },
};

// Slice
const documentsSlice = createSlice({
  name: 'documents',
  initialState,
  reducers: {
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    setPagination: (state, action) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
    clearCurrentDocument: (state) => {
      state.currentDocument = null;
    },
    clearError: (state) => {
      state.error = null;
    },
    setUploadProgress: (state, action) => {
      const { fileId, progress } = action.payload;
      state.uploadProgress[fileId] = progress;
    },
    clearUploadProgress: (state, action) => {
      delete state.uploadProgress[action.payload];
    },
    clearSearchResults: (state) => {
      state.searchResults = [];
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch documents
      .addCase(fetchDocuments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocuments.fulfilled, (state, action) => {
        state.loading = false;
        state.documents = action.payload.results || action.payload;
        state.pagination = {
          page: action.payload.page || 1,
          pageSize: action.payload.page_size || 10,
          total: action.payload.count || action.payload.length,
          totalPages: action.payload.total_pages || 1,
        };
      })
      .addCase(fetchDocuments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch document by ID
      .addCase(fetchDocumentById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocumentById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentDocument = action.payload;
      })
      .addCase(fetchDocumentById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Upload document
      .addCase(uploadDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        state.loading = false;
        state.documents.unshift(action.payload);
      })
      .addCase(uploadDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Delete document
      .addCase(deleteDocument.fulfilled, (state, action) => {
        state.documents = state.documents.filter((d) => d.id !== action.payload);
      })

      // Extract document data
      .addCase(extractDocumentData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(extractDocumentData.fulfilled, (state, action) => {
        state.loading = false;
        const document = state.documents.find((d) => d.id === action.payload.id);
        if (document) {
          document.extraction = action.payload.data;
        }
        if (state.currentDocument?.id === action.payload.id) {
          state.currentDocument.extraction = action.payload.data;
        }
      })
      .addCase(extractDocumentData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Search documents
      .addCase(searchDocuments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchDocuments.fulfilled, (state, action) => {
        state.loading = false;
        state.searchResults = action.payload;
      })
      .addCase(searchDocuments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const {
  setFilters,
  setPagination,
  clearCurrentDocument,
  clearError,
  setUploadProgress,
  clearUploadProgress,
  clearSearchResults,
} = documentsSlice.actions;

export default documentsSlice.reducer;
