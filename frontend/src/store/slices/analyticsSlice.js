import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import analyticsService from '@/services/analyticsService';

// Async thunks
export const fetchDashboardMetrics = createAsyncThunk(
  'analytics/fetchDashboard',
  async (params, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getDashboardMetrics(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch dashboard metrics');
    }
  }
);

export const fetchWorkflowMetrics = createAsyncThunk(
  'analytics/fetchWorkflowMetrics',
  async (params, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getWorkflowMetrics(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch workflow metrics');
    }
  }
);

export const fetchExecutionMetrics = createAsyncThunk(
  'analytics/fetchExecutionMetrics',
  async (params, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getExecutionMetrics(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch execution metrics');
    }
  }
);

export const fetchAIUsageMetrics = createAsyncThunk(
  'analytics/fetchAIUsage',
  async (params, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getAIUsageMetrics(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch AI usage metrics');
    }
  }
);

export const fetchUserActivityMetrics = createAsyncThunk(
  'analytics/fetchUserActivity',
  async (params, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getUserActivityMetrics(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch user activity');
    }
  }
);

export const fetchErrorMetrics = createAsyncThunk(
  'analytics/fetchErrors',
  async (params, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getErrorMetrics(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch error metrics');
    }
  }
);

export const fetchPerformanceMetrics = createAsyncThunk(
  'analytics/fetchPerformance',
  async (params, { rejectWithValue }) => {
    try {
      const response = await analyticsService.getPerformanceMetrics(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch performance metrics');
    }
  }
);

export const exportReport = createAsyncThunk(
  'analytics/exportReport',
  async ({ type, format, params }, { rejectWithValue }) => {
    try {
      const response = await analyticsService.exportReport(type, format, params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to export report');
    }
  }
);

// Initial state
const initialState = {
  dashboard: {
    totalWorkflows: 0,
    totalExecutions: 0,
    successRate: 0,
    aiTokensUsed: 0,
    activeUsers: 0,
  },
  workflowMetrics: {
    byStatus: [],
    byCategory: [],
    mostUsed: [],
    successRates: [],
  },
  executionMetrics: {
    timeline: [],
    statusDistribution: [],
    averageDuration: 0,
    totalExecutions: 0,
  },
  aiUsageMetrics: {
    timeline: [],
    byModel: [],
    totalTokens: 0,
    totalCost: 0,
  },
  userActivityMetrics: {
    activeUsers: [],
    loginTrends: [],
    featureUsage: [],
  },
  errorMetrics: {
    topErrors: [],
    errorRate: 0,
    errorTimeline: [],
  },
  performanceMetrics: {
    latency: { p50: 0, p95: 0, p99: 0 },
    throughput: 0,
  },
  loading: false,
  error: null,
  dateRange: {
    start: null,
    end: null,
  },
};

// Slice
const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    setDateRange: (state, action) => {
      state.dateRange = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch dashboard metrics
      .addCase(fetchDashboardMetrics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboardMetrics.fulfilled, (state, action) => {
        state.loading = false;
        state.dashboard = action.payload;
      })
      .addCase(fetchDashboardMetrics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch workflow metrics
      .addCase(fetchWorkflowMetrics.fulfilled, (state, action) => {
        state.workflowMetrics = action.payload;
      })

      // Fetch execution metrics
      .addCase(fetchExecutionMetrics.fulfilled, (state, action) => {
        state.executionMetrics = action.payload;
      })

      // Fetch AI usage metrics
      .addCase(fetchAIUsageMetrics.fulfilled, (state, action) => {
        state.aiUsageMetrics = action.payload;
      })

      // Fetch user activity metrics
      .addCase(fetchUserActivityMetrics.fulfilled, (state, action) => {
        state.userActivityMetrics = action.payload;
      })

      // Fetch error metrics
      .addCase(fetchErrorMetrics.fulfilled, (state, action) => {
        state.errorMetrics = action.payload;
      })

      // Fetch performance metrics
      .addCase(fetchPerformanceMetrics.fulfilled, (state, action) => {
        state.performanceMetrics = action.payload;
      })

      // Export report
      .addCase(exportReport.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(exportReport.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(exportReport.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { setDateRange, clearError } = analyticsSlice.actions;

export default analyticsSlice.reducer;
