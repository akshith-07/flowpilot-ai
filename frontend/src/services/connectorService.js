import api from './api';
import { CONNECTOR_ENDPOINTS } from '@/constants/apiEndpoints';

/**
 * Connector Service
 * Handles all connector-related API calls
 */
const connectorService = {
  /**
   * Get all connectors
   * @returns {Promise}
   */
  getConnectors: () => {
    return api.get(CONNECTOR_ENDPOINTS.LIST);
  },

  /**
   * Get connector by ID
   * @param {string} id - Connector ID
   * @returns {Promise}
   */
  getConnectorById: (id) => {
    return api.get(CONNECTOR_ENDPOINTS.DETAIL(id));
  },

  /**
   * Get available connector types
   * @returns {Promise}
   */
  getAvailableConnectors: () => {
    return api.get(CONNECTOR_ENDPOINTS.AVAILABLE);
  },

  /**
   * Authorize a connector (OAuth flow)
   * @param {string} provider - Provider name (e.g., 'gmail', 'slack')
   * @param {string} redirectUrl - URL to redirect after authorization
   * @returns {Promise}
   */
  authorizeConnector: (provider, redirectUrl) => {
    return api.post(CONNECTOR_ENDPOINTS.AUTHORIZE(provider), { redirect_url: redirectUrl });
  },

  /**
   * Handle OAuth callback
   * @param {string} provider - Provider name
   * @param {Object} params - Callback parameters (code, state, etc.)
   * @returns {Promise}
   */
  handleOAuthCallback: (provider, params) => {
    return api.post(CONNECTOR_ENDPOINTS.CALLBACK(provider), params);
  },

  /**
   * Disconnect a connector
   * @param {string} id - Connector ID
   * @returns {Promise}
   */
  disconnectConnector: (id) => {
    return api.delete(CONNECTOR_ENDPOINTS.DETAIL(id));
  },

  /**
   * Test connector connection
   * @param {string} id - Connector ID
   * @returns {Promise}
   */
  testConnection: (id) => {
    return api.post(CONNECTOR_ENDPOINTS.TEST(id));
  },

  /**
   * Update connector settings
   * @param {string} id - Connector ID
   * @param {Object} settings - Settings to update
   * @returns {Promise}
   */
  updateConnectorSettings: (id, settings) => {
    return api.patch(CONNECTOR_ENDPOINTS.DETAIL(id), settings);
  },

  /**
   * Sync connector data
   * @param {string} id - Connector ID
   * @returns {Promise}
   */
  syncConnector: (id) => {
    return api.post(CONNECTOR_ENDPOINTS.SYNC(id));
  },

  /**
   * Get connector webhooks
   * @param {string} id - Connector ID
   * @returns {Promise}
   */
  getWebhooks: (id) => {
    return api.get(CONNECTOR_ENDPOINTS.WEBHOOKS(id));
  },

  /**
   * Register webhook for connector
   * @param {string} id - Connector ID
   * @param {Object} webhookData - Webhook configuration
   * @returns {Promise}
   */
  registerWebhook: (id, webhookData) => {
    return api.post(CONNECTOR_ENDPOINTS.WEBHOOKS(id), webhookData);
  },
};

export default connectorService;
