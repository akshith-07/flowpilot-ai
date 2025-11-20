/**
 * API Endpoints
 * Centralized API endpoint definitions for all features
 */

export const AUTH_ENDPOINTS = {
  login: '/auth/login',
  register: '/auth/register',
  logout: '/auth/logout',
  refresh: '/auth/refresh',
  passwordReset: '/auth/password-reset',
  passwordResetConfirm: '/auth/password-reset-confirm',
  mfaSetup: '/auth/mfa/setup',
  mfaVerify: '/auth/mfa/verify',
  mfaDisable: '/auth/mfa/disable',
  me: '/auth/me',
};

export const USER_ENDPOINTS = {
  list: '/users',
  detail: (id) => `/users/${id}`,
  update: (id) => `/users/${id}`,
  delete: (id) => `/users/${id}`,
  profile: '/users/me',
  updateProfile: '/users/me',
  changePassword: '/users/me/password',
  settings: '/users/me/settings',
  updateSettings: '/users/me/settings',
  sessions: '/users/me/sessions',
  terminateSession: (id) => `/users/me/sessions/${id}`,
};

export const ORGANIZATION_ENDPOINTS = {
  list: '/organizations',
  detail: (id) => `/organizations/${id}`,
  create: '/organizations',
  update: (id) => `/organizations/${id}`,
  delete: (id) => `/organizations/${id}`,
  members: (id) => `/organizations/${id}/members`,
  addMember: (id) => `/organizations/${id}/members`,
  updateMember: (orgId, memberId) => `/organizations/${orgId}/members/${memberId}`,
  removeMember: (orgId, memberId) => `/organizations/${orgId}/members/${memberId}`,
  invitations: (id) => `/organizations/${id}/invitations`,
  sendInvitation: (id) => `/organizations/${id}/invitations`,
  cancelInvitation: (orgId, invitationId) => `/organizations/${orgId}/invitations/${invitationId}`,
  roles: (id) => `/organizations/${id}/roles`,
  createRole: (id) => `/organizations/${id}/roles`,
  updateRole: (orgId, roleId) => `/organizations/${orgId}/roles/${roleId}`,
  deleteRole: (orgId, roleId) => `/organizations/${orgId}/roles/${roleId}`,
  settings: (id) => `/organizations/${id}/settings`,
  updateSettings: (id) => `/organizations/${id}/settings`,
  apiKeys: (id) => `/organizations/${id}/api-keys`,
  createApiKey: (id) => `/organizations/${id}/api-keys`,
  revokeApiKey: (orgId, keyId) => `/organizations/${orgId}/api-keys/${keyId}`,
  usage: (id) => `/organizations/${id}/usage`,
};

export const WORKFLOW_ENDPOINTS = {
  list: '/workflows',
  detail: (id) => `/workflows/${id}`,
  create: '/workflows',
  update: (id) => `/workflows/${id}`,
  delete: (id) => `/workflows/${id}`,
  duplicate: (id) => `/workflows/${id}/duplicate`,
  versions: (id) => `/workflows/${id}/versions`,
  versionDetail: (workflowId, versionId) => `/workflows/${workflowId}/versions/${versionId}`,
  restoreVersion: (workflowId, versionId) => `/workflows/${workflowId}/versions/${versionId}/restore`,
  templates: '/workflows/templates',
  templateDetail: (id) => `/workflows/templates/${id}`,
  createFromTemplate: '/workflows/from-template',
  test: (id) => `/workflows/${id}/test`,
  validate: (id) => `/workflows/${id}/validate`,
  export: (id) => `/workflows/${id}/export`,
  import: '/workflows/import',
};

export const EXECUTION_ENDPOINTS = {
  list: '/executions',
  detail: (id) => `/executions/${id}`,
  create: '/executions',
  cancel: (id) => `/executions/${id}/cancel`,
  retry: (id) => `/executions/${id}/retry`,
  logs: (id) => `/executions/${id}/logs`,
  steps: (id) => `/executions/${id}/steps`,
  stepDetail: (executionId, stepId) => `/executions/${executionId}/steps/${stepId}`,
  output: (id) => `/executions/${id}/output`,
  metrics: (id) => `/executions/${id}/metrics`,
};

export const CONNECTOR_ENDPOINTS = {
  list: '/connectors',
  detail: (id) => `/connectors/${id}`,
  create: '/connectors',
  update: (id) => `/connectors/${id}`,
  delete: (id) => `/connectors/${id}`,
  authorize: (id) => `/connectors/${id}/authorize`,
  disconnect: (id) => `/connectors/${id}/disconnect`,
  test: (id) => `/connectors/${id}/test`,
  webhooks: (id) => `/connectors/${id}/webhooks`,
  createWebhook: (id) => `/connectors/${id}/webhooks`,
  deleteWebhook: (connectorId, webhookId) => `/connectors/${connectorId}/webhooks/${webhookId}`,
  sync: (id) => `/connectors/${id}/sync`,
  syncLogs: (id) => `/connectors/${id}/sync-logs`,
  providers: '/connectors/providers',
};

export const DOCUMENT_ENDPOINTS = {
  list: '/documents',
  detail: (id) => `/documents/${id}`,
  upload: '/documents/upload',
  uploadMultiple: '/documents/upload-multiple',
  delete: (id) => `/documents/${id}`,
  download: (id) => `/documents/${id}/download`,
  extract: (id) => `/documents/${id}/extract`,
  extractions: (id) => `/documents/${id}/extractions`,
  search: '/documents/search',
  semanticSearch: '/documents/semantic-search',
  pages: (id) => `/documents/${id}/pages`,
  versions: (id) => `/documents/${id}/versions`,
  process: (id) => `/documents/${id}/process`,
  batchProcess: '/documents/batch-process',
};

export const ANALYTICS_ENDPOINTS = {
  dashboard: '/analytics/dashboard',
  workflows: '/analytics/workflows',
  workflowDetail: (id) => `/analytics/workflows/${id}`,
  executions: '/analytics/executions',
  aiUsage: '/analytics/ai-usage',
  errors: '/analytics/errors',
  users: '/analytics/users',
  performance: '/analytics/performance',
  export: '/analytics/export',
  reports: '/analytics/reports',
  createReport: '/analytics/reports',
  reportDetail: (id) => `/analytics/reports/${id}`,
  scheduleReport: (id) => `/analytics/reports/${id}/schedule`,
};

export const NOTIFICATION_ENDPOINTS = {
  list: '/notifications',
  detail: (id) => `/notifications/${id}`,
  markRead: (id) => `/notifications/${id}/read`,
  markAllRead: '/notifications/read-all',
  delete: (id) => `/notifications/${id}`,
  deleteAll: '/notifications/delete-all',
  preferences: '/notifications/preferences',
  updatePreferences: '/notifications/preferences',
  unreadCount: '/notifications/unread-count',
};

export const AUDIT_ENDPOINTS = {
  list: '/audit-logs',
  detail: (id) => `/audit-logs/${id}`,
  export: '/audit-logs/export',
  filter: '/audit-logs/filter',
};

export const BILLING_ENDPOINTS = {
  usage: '/billing/usage',
  invoices: '/billing/invoices',
  invoiceDetail: (id) => `/billing/invoices/${id}`,
  paymentMethods: '/billing/payment-methods',
  addPaymentMethod: '/billing/payment-methods',
  deletePaymentMethod: (id) => `/billing/payment-methods/${id}`,
  subscription: '/billing/subscription',
  updateSubscription: '/billing/subscription',
  plans: '/billing/plans',
};
