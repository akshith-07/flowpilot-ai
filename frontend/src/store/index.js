/**
 * Redux Store Configuration
 * Configures and exports the Redux store
 */

import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';

/**
 * Configure store with all reducers
 */
export const store = configureStore({
  reducer: {
    auth: authReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['your/action/type'],
        // Ignore these field paths in all actions
        ignoredActionPaths: ['meta.arg', 'payload.timestamp'],
        // Ignore these paths in the state
        ignoredPaths: ['items.dates'],
      },
    }),
  devTools: import.meta.env.MODE !== 'production',
});

export default store;
