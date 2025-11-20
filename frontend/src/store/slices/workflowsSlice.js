import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import workflowService from '@/services/workflowService';

// Async thunks
export const fetchWorkflows = createAsyncThunk(
  'workflows/fetchAll',
  async (params, { rejectWithValue }) => {
    try {
      const response = await workflowService.getWorkflows(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch workflows');
    }
  }
);

export const fetchWorkflowById = createAsyncThunk(
  'workflows/fetchById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await workflowService.getWorkflowById(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch workflow');
    }
  }
);

export const createWorkflow = createAsyncThunk(
  'workflows/create',
  async (workflowData, { rejectWithValue }) => {
    try {
      const response = await workflowService.createWorkflow(workflowData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create workflow');
    }
  }
);

export const updateWorkflow = createAsyncThunk(
  'workflows/update',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await workflowService.updateWorkflow(id, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update workflow');
    }
  }
);

export const deleteWorkflow = createAsyncThunk(
  'workflows/delete',
  async (id, { rejectWithValue }) => {
    try {
      await workflowService.deleteWorkflow(id);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to delete workflow');
    }
  }
);

export const duplicateWorkflow = createAsyncThunk(
  'workflows/duplicate',
  async (id, { rejectWithValue }) => {
    try {
      const response = await workflowService.duplicateWorkflow(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to duplicate workflow');
    }
  }
);

export const executeWorkflow = createAsyncThunk(
  'workflows/execute',
  async ({ id, input }, { rejectWithValue }) => {
    try {
      const response = await workflowService.executeWorkflow(id, input);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to execute workflow');
    }
  }
);

export const testWorkflow = createAsyncThunk(
  'workflows/test',
  async ({ id, input }, { rejectWithValue }) => {
    try {
      const response = await workflowService.testWorkflow(id, input);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to test workflow');
    }
  }
);

export const fetchWorkflowVersions = createAsyncThunk(
  'workflows/fetchVersions',
  async (id, { rejectWithValue }) => {
    try {
      const response = await workflowService.getWorkflowVersions(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch versions');
    }
  }
);

export const fetchWorkflowExecutions = createAsyncThunk(
  'workflows/fetchExecutions',
  async (id, { rejectWithValue }) => {
    try {
      const response = await workflowService.getWorkflowExecutions(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch executions');
    }
  }
);

// Initial state
const initialState = {
  workflows: [],
  currentWorkflow: null,
  versions: [],
  executions: [],
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
    status: '',
    category: '',
  },
};

// Slice
const workflowsSlice = createSlice({
  name: 'workflows',
  initialState,
  reducers: {
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    setPagination: (state, action) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
    clearCurrentWorkflow: (state) => {
      state.currentWorkflow = null;
      state.versions = [];
      state.executions = [];
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch workflows
      .addCase(fetchWorkflows.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchWorkflows.fulfilled, (state, action) => {
        state.loading = false;
        state.workflows = action.payload.results || action.payload;
        state.pagination = {
          page: action.payload.page || 1,
          pageSize: action.payload.page_size || 10,
          total: action.payload.count || action.payload.length,
          totalPages: action.payload.total_pages || 1,
        };
      })
      .addCase(fetchWorkflows.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch workflow by ID
      .addCase(fetchWorkflowById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchWorkflowById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentWorkflow = action.payload;
      })
      .addCase(fetchWorkflowById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Create workflow
      .addCase(createWorkflow.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createWorkflow.fulfilled, (state, action) => {
        state.loading = false;
        state.workflows.unshift(action.payload);
      })
      .addCase(createWorkflow.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Update workflow
      .addCase(updateWorkflow.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateWorkflow.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.workflows.findIndex((w) => w.id === action.payload.id);
        if (index !== -1) {
          state.workflows[index] = action.payload;
        }
        if (state.currentWorkflow?.id === action.payload.id) {
          state.currentWorkflow = action.payload;
        }
      })
      .addCase(updateWorkflow.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Delete workflow
      .addCase(deleteWorkflow.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteWorkflow.fulfilled, (state, action) => {
        state.loading = false;
        state.workflows = state.workflows.filter((w) => w.id !== action.payload);
      })
      .addCase(deleteWorkflow.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Duplicate workflow
      .addCase(duplicateWorkflow.fulfilled, (state, action) => {
        state.workflows.unshift(action.payload);
      })

      // Execute workflow
      .addCase(executeWorkflow.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(executeWorkflow.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(executeWorkflow.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Test workflow
      .addCase(testWorkflow.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(testWorkflow.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(testWorkflow.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch versions
      .addCase(fetchWorkflowVersions.fulfilled, (state, action) => {
        state.versions = action.payload;
      })

      // Fetch executions
      .addCase(fetchWorkflowExecutions.fulfilled, (state, action) => {
        state.executions = action.payload.results || action.payload;
      });
  },
});

export const { setFilters, setPagination, clearCurrentWorkflow, clearError } = workflowsSlice.actions;

export default workflowsSlice.reducer;
