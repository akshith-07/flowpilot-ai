import api from './api';
import { ANALYTICS_ENDPOINTS } from '@/constants/apiEndpoints';

/**
 * Analytics Service
 * Handles all analytics-related API calls
 */
const analyticsService = {
  /**
   * Get dashboard metrics
   * @param {Object} params - Query parameters (date range, etc.)
   * @returns {Promise}
   */
  getDashboardMetrics: (params = {}) => {
    return api.get(ANALYTICS_ENDPOINTS.DASHBOARD, { params });
  },

  /**
   * Get workflow metrics
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getWorkflowMetrics: (params = {}) => {
    return api.get(ANALYTICS_ENDPOINTS.WORKFLOW_METRICS, { params });
  },

  /**
   * Get execution metrics
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getExecutionMetrics: (params = {}) => {
    return api.get(ANALYTICS_ENDPOINTS.EXECUTION_METRICS, { params });
  },

  /**
   * Get AI usage metrics
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getAIUsageMetrics: (params = {}) => {
    return api.get(ANALYTICS_ENDPOINTS.AI_USAGE, { params });
  },

  /**
   * Get user activity metrics
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getUserActivityMetrics: (params = {}) => {
    return api.get(ANALYTICS_ENDPOINTS.USER_ACTIVITY, { params });
  },

  /**
   * Get error metrics
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getErrorMetrics: (params = {}) => {
    return api.get(ANALYTICS_ENDPOINTS.ERROR_METRICS, { params });
  },

  /**
   * Get performance metrics
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getPerformanceMetrics: (params = {}) => {
    return api.get(ANALYTICS_ENDPOINTS.PERFORMANCE_METRICS, { params });
  },

  /**
   * Get connector usage metrics
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getConnectorUsage: (params = {}) => {
    return api.get(ANALYTICS_ENDPOINTS.CONNECTOR_USAGE, { params });
  },

  /**
   * Get document processing metrics
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getDocumentMetrics: (params = {}) => {
    return api.get(ANALYTICS_ENDPOINTS.DOCUMENT_METRICS, { params });
  },

  /**
   * Get custom report
   * @param {string} reportId - Report ID
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getCustomReport: (reportId, params = {}) => {
    return api.get(ANALYTICS_ENDPOINTS.CUSTOM_REPORT(reportId), { params });
  },

  /**
   * Export report
   * @param {string} type - Report type
   * @param {string} format - Export format (csv, excel, pdf)
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  exportReport: (type, format = 'csv', params = {}) => {
    return api.download(ANALYTICS_ENDPOINTS.EXPORT, {
      type,
      format,
      ...params,
    });
  },
};

export default analyticsService;
