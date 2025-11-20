/**
 * Workflow Service
 * Handles all workflow-related API calls
 */

import { get, post, put, patch, del } from './api';
import { WORKFLOW_ENDPOINTS } from '@constants';

/**
 * Get all workflows with pagination and filters
 * @param {object} params - Query parameters (page, limit, search, status, etc.)
 * @returns {Promise} Response promise
 */
export const getWorkflows = async (params = {}) => {
  const response = await get(WORKFLOW_ENDPOINTS.list, { params });
  return response.data;
};

/**
 * Get workflow by ID
 * @param {string} id - Workflow ID
 * @returns {Promise} Response promise
 */
export const getWorkflow = async (id) => {
  const response = await get(WORKFLOW_ENDPOINTS.detail(id));
  return response.data;
};

/**
 * Create new workflow
 * @param {object} data - Workflow data
 * @returns {Promise} Response promise
 */
export const createWorkflow = async (data) => {
  const response = await post(WORKFLOW_ENDPOINTS.create, data);
  return response.data;
};

/**
 * Update workflow
 * @param {string} id - Workflow ID
 * @param {object} data - Updated workflow data
 * @returns {Promise} Response promise
 */
export const updateWorkflow = async (id, data) => {
  const response = await put(WORKFLOW_ENDPOINTS.update(id), data);
  return response.data;
};

/**
 * Delete workflow
 * @param {string} id - Workflow ID
 * @returns {Promise} Response promise
 */
export const deleteWorkflow = async (id) => {
  const response = await del(WORKFLOW_ENDPOINTS.delete(id));
  return response.data;
};

/**
 * Duplicate workflow
 * @param {string} id - Workflow ID
 * @returns {Promise} Response promise
 */
export const duplicateWorkflow = async (id) => {
  const response = await post(WORKFLOW_ENDPOINTS.duplicate(id));
  return response.data;
};

/**
 * Get workflow versions
 * @param {string} id - Workflow ID
 * @returns {Promise} Response promise
 */
export const getWorkflowVersions = async (id) => {
  const response = await get(WORKFLOW_ENDPOINTS.versions(id));
  return response.data;
};

/**
 * Get specific workflow version
 * @param {string} workflowId - Workflow ID
 * @param {string} versionId - Version ID
 * @returns {Promise} Response promise
 */
export const getWorkflowVersion = async (workflowId, versionId) => {
  const response = await get(WORKFLOW_ENDPOINTS.versionDetail(workflowId, versionId));
  return response.data;
};

/**
 * Restore workflow version
 * @param {string} workflowId - Workflow ID
 * @param {string} versionId - Version ID
 * @returns {Promise} Response promise
 */
export const restoreWorkflowVersion = async (workflowId, versionId) => {
  const response = await post(WORKFLOW_ENDPOINTS.restoreVersion(workflowId, versionId));
  return response.data;
};

/**
 * Get workflow templates
 * @returns {Promise} Response promise
 */
export const getWorkflowTemplates = async () => {
  const response = await get(WORKFLOW_ENDPOINTS.templates);
  return response.data;
};

/**
 * Get workflow template by ID
 * @param {string} id - Template ID
 * @returns {Promise} Response promise
 */
export const getWorkflowTemplate = async (id) => {
  const response = await get(WORKFLOW_ENDPOINTS.templateDetail(id));
  return response.data;
};

/**
 * Create workflow from template
 * @param {object} data - Template data with customizations
 * @returns {Promise} Response promise
 */
export const createWorkflowFromTemplate = async (data) => {
  const response = await post(WORKFLOW_ENDPOINTS.createFromTemplate, data);
  return response.data;
};

/**
 * Test workflow
 * @param {string} id - Workflow ID
 * @param {object} testData - Test input data
 * @returns {Promise} Response promise
 */
export const testWorkflow = async (id, testData) => {
  const response = await post(WORKFLOW_ENDPOINTS.test(id), testData);
  return response.data;
};

/**
 * Validate workflow
 * @param {string} id - Workflow ID
 * @returns {Promise} Response promise
 */
export const validateWorkflow = async (id) => {
  const response = await post(WORKFLOW_ENDPOINTS.validate(id));
  return response.data;
};

/**
 * Export workflow
 * @param {string} id - Workflow ID
 * @returns {Promise} Response promise
 */
export const exportWorkflow = async (id) => {
  const response = await get(WORKFLOW_ENDPOINTS.export(id));
  return response.data;
};

/**
 * Import workflow
 * @param {object} data - Workflow import data
 * @returns {Promise} Response promise
 */
export const importWorkflow = async (data) => {
  const response = await post(WORKFLOW_ENDPOINTS.import, data);
  return response.data;
};

export default {
  getWorkflows,
  getWorkflow,
  createWorkflow,
  updateWorkflow,
  deleteWorkflow,
  duplicateWorkflow,
  getWorkflowVersions,
  getWorkflowVersion,
  restoreWorkflowVersion,
  getWorkflowTemplates,
  getWorkflowTemplate,
  createWorkflowFromTemplate,
  testWorkflow,
  validateWorkflow,
  exportWorkflow,
  importWorkflow,
};
