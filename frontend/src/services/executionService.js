import api from './api';
import { EXECUTION_ENDPOINTS } from '@/constants/apiEndpoints';

/**
 * Execution Service
 * Handles all execution-related API calls
 */
const executionService = {
  /**
   * Get all executions
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getExecutions: (params = {}) => {
    return api.get(EXECUTION_ENDPOINTS.LIST, { params });
  },

  /**
   * Get execution by ID
   * @param {string} id - Execution ID
   * @returns {Promise}
   */
  getExecutionById: (id) => {
    return api.get(EXECUTION_ENDPOINTS.DETAIL(id));
  },

  /**
   * Cancel execution
   * @param {string} id - Execution ID
   * @returns {Promise}
   */
  cancelExecution: (id) => {
    return api.post(EXECUTION_ENDPOINTS.CANCEL(id));
  },

  /**
   * Retry execution
   * @param {string} id - Execution ID
   * @returns {Promise}
   */
  retryExecution: (id) => {
    return api.post(EXECUTION_ENDPOINTS.RETRY(id));
  },

  /**
   * Get execution logs
   * @param {string} id - Execution ID
   * @returns {Promise}
   */
  getExecutionLogs: (id) => {
    return api.get(EXECUTION_ENDPOINTS.LOGS(id));
  },

  /**
   * Get execution steps
   * @param {string} id - Execution ID
   * @returns {Promise}
   */
  getExecutionSteps: (id) => {
    return api.get(EXECUTION_ENDPOINTS.STEPS(id));
  },

  /**
   * Get execution output
   * @param {string} id - Execution ID
   * @returns {Promise}
   */
  getExecutionOutput: (id) => {
    return api.get(EXECUTION_ENDPOINTS.OUTPUT(id));
  },

  /**
   * Get execution metrics
   * @param {string} id - Execution ID
   * @returns {Promise}
   */
  getExecutionMetrics: (id) => {
    return api.get(EXECUTION_ENDPOINTS.METRICS(id));
  },

  /**
   * Export execution data
   * @param {string} id - Execution ID
   * @param {string} format - Export format (json, csv, pdf)
   * @returns {Promise}
   */
  exportExecution: (id, format = 'json') => {
    return api.download(EXECUTION_ENDPOINTS.EXPORT(id), { format });
  },
};

export default executionService;
