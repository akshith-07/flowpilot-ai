import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import executionService from '@/services/executionService';

// Async thunks
export const fetchExecutions = createAsyncThunk(
  'executions/fetchAll',
  async (params, { rejectWithValue }) => {
    try {
      const response = await executionService.getExecutions(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch executions');
    }
  }
);

export const fetchExecutionById = createAsyncThunk(
  'executions/fetchById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await executionService.getExecutionById(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch execution');
    }
  }
);

export const retryExecution = createAsyncThunk(
  'executions/retry',
  async (id, { rejectWithValue }) => {
    try {
      const response = await executionService.retryExecution(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to retry execution');
    }
  }
);

export const cancelExecution = createAsyncThunk(
  'executions/cancel',
  async (id, { rejectWithValue }) => {
    try {
      const response = await executionService.cancelExecution(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to cancel execution');
    }
  }
);

export const fetchExecutionLogs = createAsyncThunk(
  'executions/fetchLogs',
  async (id, { rejectWithValue }) => {
    try {
      const response = await executionService.getExecutionLogs(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch logs');
    }
  }
);

export const fetchExecutionSteps = createAsyncThunk(
  'executions/fetchSteps',
  async (id, { rejectWithValue }) => {
    try {
      const response = await executionService.getExecutionSteps(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch steps');
    }
  }
);

// Initial state
const initialState = {
  executions: [],
  currentExecution: null,
  logs: [],
  steps: [],
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
    workflow: '',
    dateFrom: '',
    dateTo: '',
  },
};

// Slice
const executionsSlice = createSlice({
  name: 'executions',
  initialState,
  reducers: {
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    setPagination: (state, action) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
    clearCurrentExecution: (state) => {
      state.currentExecution = null;
      state.logs = [];
      state.steps = [];
    },
    clearError: (state) => {
      state.error = null;
    },
    updateExecutionStatus: (state, action) => {
      const { id, status } = action.payload;
      const execution = state.executions.find((e) => e.id === id);
      if (execution) {
        execution.status = status;
      }
      if (state.currentExecution?.id === id) {
        state.currentExecution.status = status;
      }
    },
    addExecutionLog: (state, action) => {
      state.logs.push(action.payload);
    },
    updateExecutionStep: (state, action) => {
      const { stepId, data } = action.payload;
      const step = state.steps.find((s) => s.id === stepId);
      if (step) {
        Object.assign(step, data);
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch executions
      .addCase(fetchExecutions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchExecutions.fulfilled, (state, action) => {
        state.loading = false;
        state.executions = action.payload.results || action.payload;
        state.pagination = {
          page: action.payload.page || 1,
          pageSize: action.payload.page_size || 10,
          total: action.payload.count || action.payload.length,
          totalPages: action.payload.total_pages || 1,
        };
      })
      .addCase(fetchExecutions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch execution by ID
      .addCase(fetchExecutionById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchExecutionById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentExecution = action.payload;
      })
      .addCase(fetchExecutionById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Retry execution
      .addCase(retryExecution.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(retryExecution.fulfilled, (state, action) => {
        state.loading = false;
        state.executions.unshift(action.payload);
      })
      .addCase(retryExecution.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Cancel execution
      .addCase(cancelExecution.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(cancelExecution.fulfilled, (state, action) => {
        state.loading = false;
        const execution = state.executions.find((e) => e.id === action.payload.id);
        if (execution) {
          execution.status = 'cancelled';
        }
        if (state.currentExecution?.id === action.payload.id) {
          state.currentExecution.status = 'cancelled';
        }
      })
      .addCase(cancelExecution.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch logs
      .addCase(fetchExecutionLogs.fulfilled, (state, action) => {
        state.logs = action.payload;
      })

      // Fetch steps
      .addCase(fetchExecutionSteps.fulfilled, (state, action) => {
        state.steps = action.payload;
      });
  },
});

export const {
  setFilters,
  setPagination,
  clearCurrentExecution,
  clearError,
  updateExecutionStatus,
  addExecutionLog,
  updateExecutionStep,
} = executionsSlice.actions;

export default executionsSlice.reducer;
