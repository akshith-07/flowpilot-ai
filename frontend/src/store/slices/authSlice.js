/**
 * Auth Slice
 * Redux slice for authentication state management
 */

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { authService } from '@services';
import { getUser, getAccessToken, getRefreshToken } from '@utils';

/**
 * Initial state
 */
const initialState = {
  user: getUser(),
  isAuthenticated: !!getAccessToken(),
  loading: false,
  error: null,
  mfaRequired: false,
  mfaSetupData: null,
};

/**
 * Async thunks
 */

export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const data = await authService.login(credentials);
      return data;
    } catch (error) {
      return rejectWithValue(error.message || 'Login failed');
    }
  }
);

export const registerUser = createAsyncThunk(
  'auth/register',
  async (userData, { rejectWithValue }) => {
    try {
      const data = await authService.register(userData);
      return data;
    } catch (error) {
      return rejectWithValue(error.message || 'Registration failed');
    }
  }
);

export const logoutUser = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await authService.logout();
      return null;
    } catch (error) {
      return rejectWithValue(error.message || 'Logout failed');
    }
  }
);

export const fetchCurrentUser = createAsyncThunk(
  'auth/fetchCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const data = await authService.getCurrentUser();
      return data;
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to fetch user');
    }
  }
);

export const requestPasswordReset = createAsyncThunk(
  'auth/requestPasswordReset',
  async (email, { rejectWithValue }) => {
    try {
      const data = await authService.requestPasswordReset(email);
      return data;
    } catch (error) {
      return rejectWithValue(error.message || 'Password reset request failed');
    }
  }
);

export const confirmPasswordReset = createAsyncThunk(
  'auth/confirmPasswordReset',
  async (resetData, { rejectWithValue }) => {
    try {
      const data = await authService.confirmPasswordReset(resetData);
      return data;
    } catch (error) {
      return rejectWithValue(error.message || 'Password reset confirmation failed');
    }
  }
);

export const setupMFA = createAsyncThunk(
  'auth/setupMFA',
  async (_, { rejectWithValue }) => {
    try {
      const data = await authService.setupMFA();
      return data;
    } catch (error) {
      return rejectWithValue(error.message || 'MFA setup failed');
    }
  }
);

export const verifyMFA = createAsyncThunk(
  'auth/verifyMFA',
  async (code, { rejectWithValue }) => {
    try {
      const data = await authService.verifyMFA(code);
      return data;
    } catch (error) {
      return rejectWithValue(error.message || 'MFA verification failed');
    }
  }
);

export const disableMFA = createAsyncThunk(
  'auth/disableMFA',
  async (password, { rejectWithValue }) => {
    try {
      const data = await authService.disableMFA(password);
      return data;
    } catch (error) {
      return rejectWithValue(error.message || 'MFA disable failed');
    }
  }
);

/**
 * Auth slice
 */
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setUser: (state, action) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    clearAuth: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.error = null;
      state.mfaRequired = false;
      state.mfaSetupData = null;
    },
    setMFARequired: (state, action) => {
      state.mfaRequired = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Register
      .addCase(registerUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state) => {
        state.loading = false;
        state.error = null;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Logout
      .addCase(logoutUser.pending, (state) => {
        state.loading = true;
      })
      .addCase(logoutUser.fulfilled, (state) => {
        state.loading = false;
        state.user = null;
        state.isAuthenticated = false;
        state.error = null;
        state.mfaRequired = false;
        state.mfaSetupData = null;
      })
      .addCase(logoutUser.rejected, (state) => {
        state.loading = false;
        state.user = null;
        state.isAuthenticated = false;
      })
      // Fetch current user
      .addCase(fetchCurrentUser.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(fetchCurrentUser.rejected, (state) => {
        state.loading = false;
        state.user = null;
        state.isAuthenticated = false;
      })
      // Password reset request
      .addCase(requestPasswordReset.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(requestPasswordReset.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(requestPasswordReset.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Password reset confirm
      .addCase(confirmPasswordReset.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(confirmPasswordReset.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(confirmPasswordReset.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // MFA setup
      .addCase(setupMFA.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(setupMFA.fulfilled, (state, action) => {
        state.loading = false;
        state.mfaSetupData = action.payload;
      })
      .addCase(setupMFA.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // MFA verify
      .addCase(verifyMFA.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(verifyMFA.fulfilled, (state) => {
        state.loading = false;
        state.mfaRequired = false;
        if (state.user) {
          state.user.mfa_enabled = true;
        }
      })
      .addCase(verifyMFA.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // MFA disable
      .addCase(disableMFA.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(disableMFA.fulfilled, (state) => {
        state.loading = false;
        if (state.user) {
          state.user.mfa_enabled = false;
        }
      })
      .addCase(disableMFA.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError, setUser, clearAuth, setMFARequired } = authSlice.actions;

export const selectAuth = (state) => state.auth;
export const selectUser = (state) => state.auth.user;
export const selectIsAuthenticated = (state) => state.auth.isAuthenticated;
export const selectAuthLoading = (state) => state.auth.loading;
export const selectAuthError = (state) => state.auth.error;
export const selectMFARequired = (state) => state.auth.mfaRequired;
export const selectMFASetupData = (state) => state.auth.mfaSetupData;

export default authSlice.reducer;
