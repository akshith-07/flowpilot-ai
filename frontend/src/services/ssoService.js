/**
 * SSO API Service
 * Handles all SSO-related API calls
 */
import api from './api';

const ssoService = {
  // SSO Providers
  getProviders: async () => {
    const response = await api.get('/sso/providers/');
    return response.data;
  },

  getAvailableProviders: async (organizationId) => {
    const response = await api.get('/sso/providers/available/', {
      params: { organization_id: organizationId }
    });
    return response.data;
  },

  getProvider: async (providerId) => {
    const response = await api.get(`/sso/providers/${providerId}/`);
    return response.data;
  },

  // SSO Connections
  getConnections: async (organizationId) => {
    const response = await api.get('/sso/connections/', {
      params: { organization_id: organizationId }
    });
    return response.data;
  },

  getConnection: async (connectionId) => {
    const response = await api.get(`/sso/connections/${connectionId}/`);
    return response.data;
  },

  createConnection: async (connectionData) => {
    const response = await api.post('/sso/connections/', connectionData);
    return response.data;
  },

  updateConnection: async (connectionId, connectionData) => {
    const response = await api.put(`/sso/connections/${connectionId}/`, connectionData);
    return response.data;
  },

  deleteConnection: async (connectionId) => {
    await api.delete(`/sso/connections/${connectionId}/`);
  },

  testConnection: async (connectionId) => {
    const response = await api.post(`/sso/connections/${connectionId}/test/`);
    return response.data;
  },

  getConnectionStats: async (connectionId) => {
    const response = await api.get(`/sso/connections/${connectionId}/stats/`);
    return response.data;
  },

  activateConnection: async (connectionId) => {
    const response = await api.post(`/sso/connections/${connectionId}/activate/`);
    return response.data;
  },

  deactivateConnection: async (connectionId) => {
    const response = await api.post(`/sso/connections/${connectionId}/deactivate/`);
    return response.data;
  },

  // SSO Authentication
  initiateLogin: async (connectionId, redirectUri) => {
    const response = await api.post('/sso/login/', {
      connection_id: connectionId,
      redirect_uri: redirectUri
    });
    return response.data;
  },

  // SSO Sessions
  getSessions: async (organizationId = null) => {
    const params = organizationId ? { organization_id: organizationId } : {};
    const response = await api.get('/sso/sessions/', { params });
    return response.data;
  },

  getSession: async (sessionId) => {
    const response = await api.get(`/sso/sessions/${sessionId}/`);
    return response.data;
  },

  revokeSession: async (sessionId) => {
    const response = await api.post(`/sso/sessions/${sessionId}/revoke/`);
    return response.data;
  },

  // SSO Audit Logs
  getAuditLogs: async (filters = {}) => {
    const response = await api.get('/sso/audit-logs/', { params: filters });
    return response.data;
  },

  // SAML Metadata
  getSAMLMetadata: async (connectionId) => {
    const response = await api.get(`/sso/saml/metadata/${connectionId}/`);
    return response.data;
  }
};

export default ssoService;
