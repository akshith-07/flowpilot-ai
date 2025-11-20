import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import connectorService from '@/services/connectorService';

// Async thunks
export const fetchConnectors = createAsyncThunk(
  'connectors/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      const response = await connectorService.getConnectors();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch connectors');
    }
  }
);

export const fetchConnectorById = createAsyncThunk(
  'connectors/fetchById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await connectorService.getConnectorById(id);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch connector');
    }
  }
);

export const fetchAvailableConnectors = createAsyncThunk(
  'connectors/fetchAvailable',
  async (_, { rejectWithValue }) => {
    try {
      const response = await connectorService.getAvailableConnectors();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch available connectors');
    }
  }
);

export const authorizeConnector = createAsyncThunk(
  'connectors/authorize',
  async ({ provider, redirectUrl }, { rejectWithValue }) => {
    try {
      const response = await connectorService.authorizeConnector(provider, redirectUrl);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to authorize connector');
    }
  }
);

export const disconnectConnector = createAsyncThunk(
  'connectors/disconnect',
  async (id, { rejectWithValue }) => {
    try {
      await connectorService.disconnectConnector(id);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to disconnect connector');
    }
  }
);

export const testConnector = createAsyncThunk(
  'connectors/test',
  async (id, { rejectWithValue }) => {
    try {
      const response = await connectorService.testConnection(id);
      return { id, result: response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to test connector');
    }
  }
);

export const updateConnectorSettings = createAsyncThunk(
  'connectors/updateSettings',
  async ({ id, settings }, { rejectWithValue }) => {
    try {
      const response = await connectorService.updateConnectorSettings(id, settings);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update settings');
    }
  }
);

// Initial state
const initialState = {
  connectors: [],
  availableConnectors: [],
  currentConnector: null,
  loading: false,
  error: null,
  testResults: {},
};

// Slice
const connectorsSlice = createSlice({
  name: 'connectors',
  initialState,
  reducers: {
    clearCurrentConnector: (state) => {
      state.currentConnector = null;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearTestResult: (state, action) => {
      delete state.testResults[action.payload];
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch connectors
      .addCase(fetchConnectors.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchConnectors.fulfilled, (state, action) => {
        state.loading = false;
        state.connectors = action.payload;
      })
      .addCase(fetchConnectors.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch connector by ID
      .addCase(fetchConnectorById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchConnectorById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentConnector = action.payload;
      })
      .addCase(fetchConnectorById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch available connectors
      .addCase(fetchAvailableConnectors.fulfilled, (state, action) => {
        state.availableConnectors = action.payload;
      })

      // Authorize connector
      .addCase(authorizeConnector.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(authorizeConnector.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(authorizeConnector.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Disconnect connector
      .addCase(disconnectConnector.fulfilled, (state, action) => {
        state.connectors = state.connectors.filter((c) => c.id !== action.payload);
      })

      // Test connector
      .addCase(testConnector.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(testConnector.fulfilled, (state, action) => {
        state.loading = false;
        state.testResults[action.payload.id] = action.payload.result;
      })
      .addCase(testConnector.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Update settings
      .addCase(updateConnectorSettings.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateConnectorSettings.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.connectors.findIndex((c) => c.id === action.payload.id);
        if (index !== -1) {
          state.connectors[index] = action.payload;
        }
        if (state.currentConnector?.id === action.payload.id) {
          state.currentConnector = action.payload;
        }
      })
      .addCase(updateConnectorSettings.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearCurrentConnector, clearError, clearTestResult } = connectorsSlice.actions;

export default connectorsSlice.reducer;
