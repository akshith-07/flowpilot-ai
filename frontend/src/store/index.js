/**
 * Redux Store Configuration
 * Configures and exports the Redux store
 */

import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import workflowsReducer from './slices/workflowsSlice';
import executionsReducer from './slices/executionsSlice';
import connectorsReducer from './slices/connectorsSlice';
import documentsReducer from './slices/documentsSlice';
import analyticsReducer from './slices/analyticsSlice';
import organizationsReducer from './slices/organizationsSlice';
import notificationsReducer from './slices/notificationsSlice';

/**
 * Configure store with all reducers
 */
export const store = configureStore({
  reducer: {
    auth: authReducer,
    workflows: workflowsReducer,
    executions: executionsReducer,
    connectors: connectorsReducer,
    documents: documentsReducer,
    analytics: analyticsReducer,
    organizations: organizationsReducer,
    notifications: notificationsReducer,
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
