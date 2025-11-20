/**
 * API Service
 * Axios instance configuration with interceptors for authentication and error handling
 */

import axios from 'axios';
import { API_BASE_URL } from '@constants';
import { getAccessToken, getRefreshToken, setAccessToken, removeAuthTokens } from '@utils';

/**
 * Create Axios instance with default configuration
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Flag to prevent multiple token refresh requests
 */
let isRefreshing = false;
let failedQueue = [];

/**
 * Process failed request queue after token refresh
 * @param {Error|null} error - Error object if refresh failed
 * @param {string|null} token - New access token if refresh succeeded
 */
const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

/**
 * Request interceptor to add auth token
 */
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for error handling and token refresh
 */
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle network errors
    if (!error.response) {
      return Promise.reject({
        message: 'Network error. Please check your connection.',
        code: 'NETWORK_ERROR',
      });
    }

    // Handle 401 Unauthorized - Token expired
    if (error.response.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Add request to queue
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = getRefreshToken();

      if (!refreshToken) {
        // No refresh token, redirect to login
        removeAuthTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        // Attempt to refresh token
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        setAccessToken(access);

        // Update header and retry original request
        api.defaults.headers.common.Authorization = `Bearer ${access}`;
        originalRequest.headers.Authorization = `Bearer ${access}`;

        processQueue(null, access);

        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        processQueue(refreshError, null);
        removeAuthTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Handle 403 Forbidden
    if (error.response.status === 403) {
      return Promise.reject({
        message: 'You do not have permission to perform this action.',
        code: 'FORBIDDEN',
        data: error.response.data,
      });
    }

    // Handle 404 Not Found
    if (error.response.status === 404) {
      return Promise.reject({
        message: 'The requested resource was not found.',
        code: 'NOT_FOUND',
        data: error.response.data,
      });
    }

    // Handle 422 Validation Error
    if (error.response.status === 422) {
      return Promise.reject({
        message: 'Validation error. Please check your input.',
        code: 'VALIDATION_ERROR',
        data: error.response.data,
        errors: error.response.data.errors || {},
      });
    }

    // Handle 429 Too Many Requests
    if (error.response.status === 429) {
      return Promise.reject({
        message: 'Too many requests. Please try again later.',
        code: 'RATE_LIMIT',
        data: error.response.data,
      });
    }

    // Handle 500+ Server Errors
    if (error.response.status >= 500) {
      return Promise.reject({
        message: 'Server error. Please try again later.',
        code: 'SERVER_ERROR',
        data: error.response.data,
      });
    }

    // Default error handling
    return Promise.reject({
      message: error.response.data.message || 'An error occurred',
      code: error.response.data.code || 'UNKNOWN_ERROR',
      data: error.response.data,
    });
  }
);

/**
 * Request wrapper functions
 */

/**
 * GET request
 * @param {string} url - Request URL
 * @param {object} config - Axios config
 * @returns {Promise} Response promise
 */
export const get = (url, config = {}) => {
  return api.get(url, config);
};

/**
 * POST request
 * @param {string} url - Request URL
 * @param {object} data - Request data
 * @param {object} config - Axios config
 * @returns {Promise} Response promise
 */
export const post = (url, data = {}, config = {}) => {
  return api.post(url, data, config);
};

/**
 * PUT request
 * @param {string} url - Request URL
 * @param {object} data - Request data
 * @param {object} config - Axios config
 * @returns {Promise} Response promise
 */
export const put = (url, data = {}, config = {}) => {
  return api.put(url, data, config);
};

/**
 * PATCH request
 * @param {string} url - Request URL
 * @param {object} data - Request data
 * @param {object} config - Axios config
 * @returns {Promise} Response promise
 */
export const patch = (url, data = {}, config = {}) => {
  return api.patch(url, data, config);
};

/**
 * DELETE request
 * @param {string} url - Request URL
 * @param {object} config - Axios config
 * @returns {Promise} Response promise
 */
export const del = (url, config = {}) => {
  return api.delete(url, config);
};

/**
 * Upload file with progress tracking
 * @param {string} url - Upload URL
 * @param {FormData} formData - Form data with file
 * @param {Function} onProgress - Progress callback
 * @returns {Promise} Response promise
 */
export const upload = (url, formData, onProgress) => {
  return api.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percentCompleted);
      }
    },
  });
};

/**
 * Download file
 * @param {string} url - Download URL
 * @param {string} filename - Filename for download
 * @returns {Promise} Response promise
 */
export const download = async (url, filename) => {
  const response = await api.get(url, {
    responseType: 'blob',
  });

  const blob = new Blob([response.data]);
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);

  return response;
};

export default api;
