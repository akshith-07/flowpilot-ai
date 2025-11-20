/**
 * Application Configuration
 * Centralized configuration for the FlowPilot AI application
 */

export const APP_CONFIG = {
  name: import.meta.env.VITE_APP_NAME || 'FlowPilot AI',
  version: '1.0.0',
  environment: import.meta.env.VITE_APP_ENV || 'development',
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  apiVersion: import.meta.env.VITE_API_VERSION || 'v1',
  wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
};

export const API_BASE_URL = `${APP_CONFIG.apiUrl}/api/${APP_CONFIG.apiVersion}`;

export const STORAGE_KEYS = {
  accessToken: 'flowpilot_access_token',
  refreshToken: 'flowpilot_refresh_token',
  user: 'flowpilot_user',
  organization: 'flowpilot_organization',
  theme: 'flowpilot_theme',
  sidebarCollapsed: 'flowpilot_sidebar_collapsed',
};

export const SESSION_CONFIG = {
  timeout: parseInt(import.meta.env.VITE_SESSION_TIMEOUT) || 3600000, // 1 hour default
  refreshThreshold: 300000, // Refresh token 5 minutes before expiry
};

export const FILE_UPLOAD_CONFIG = {
  maxSize: parseInt(import.meta.env.VITE_MAX_FILE_SIZE) || 10485760, // 10MB default
  allowedTypes: (import.meta.env.VITE_ALLOWED_FILE_TYPES || '.pdf,.docx,.xlsx,.csv,.png,.jpg,.jpeg').split(','),
  maxFiles: 10,
};

export const PAGINATION_CONFIG = {
  defaultPageSize: 20,
  pageSizeOptions: [10, 20, 50, 100],
};

export const THEME_CONFIG = {
  default: 'light',
  options: ['light', 'dark'],
};

export const WORKFLOW_CONFIG = {
  maxNodes: 100,
  maxConnections: 200,
  autoSaveInterval: 30000, // 30 seconds
  executionPollingInterval: 2000, // 2 seconds
};

export const NOTIFICATION_CONFIG = {
  duration: 5000, // 5 seconds default
  position: 'top-right',
  maxNotifications: 5,
};

export const FEATURE_FLAGS = {
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  enableErrorTracking: import.meta.env.VITE_ENABLE_ERROR_TRACKING === 'true',
};
