/**
 * Route Constants
 * Centralized route path definitions
 */

export const ROUTES = {
  // Public Routes
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password/:token',
  MFA_SETUP: '/mfa-setup',
  MFA_VERIFY: '/mfa-verify',

  // Dashboard
  DASHBOARD: '/dashboard',

  // Workflows
  WORKFLOWS: '/workflows',
  WORKFLOW_CREATE: '/workflows/new',
  WORKFLOW_DETAIL: '/workflows/:id',
  WORKFLOW_EDIT: '/workflows/:id/edit',
  WORKFLOW_BUILDER: '/workflows/:id/builder',
  WORKFLOW_VERSIONS: '/workflows/:id/versions',
  WORKFLOW_TEMPLATES: '/workflows/templates',

  // Executions
  EXECUTIONS: '/executions',
  EXECUTION_DETAIL: '/executions/:id',

  // Connectors
  CONNECTORS: '/connectors',
  CONNECTOR_DETAIL: '/connectors/:id',
  CONNECTOR_AUTHORIZE: '/connectors/:id/authorize',

  // Documents
  DOCUMENTS: '/documents',
  DOCUMENT_DETAIL: '/documents/:id',
  DOCUMENT_UPLOAD: '/documents/upload',

  // Analytics
  ANALYTICS: '/analytics',
  ANALYTICS_WORKFLOWS: '/analytics/workflows',
  ANALYTICS_EXECUTIONS: '/analytics/executions',
  ANALYTICS_AI_USAGE: '/analytics/ai-usage',
  ANALYTICS_ERRORS: '/analytics/errors',

  // Organization
  ORGANIZATION_SETTINGS: '/organization/settings',
  ORGANIZATION_MEMBERS: '/organization/members',
  ORGANIZATION_ROLES: '/organization/roles',
  ORGANIZATION_API_KEYS: '/organization/api-keys',
  ORGANIZATION_BILLING: '/organization/billing',
  ORGANIZATION_AUDIT: '/organization/audit',

  // User Settings
  USER_PROFILE: '/settings/profile',
  USER_SECURITY: '/settings/security',
  USER_NOTIFICATIONS: '/settings/notifications',
  USER_SESSIONS: '/settings/sessions',

  // Other
  NOTIFICATIONS: '/notifications',
  NOT_FOUND: '*',
};

/**
 * Generate dynamic routes with parameters
 */
export const generateRoute = (route, params = {}) => {
  let path = route;
  Object.keys(params).forEach((key) => {
    path = path.replace(`:${key}`, params[key]);
  });
  return path;
};

/**
 * Route groups for navigation
 */
export const ROUTE_GROUPS = {
  AUTH: [
    ROUTES.LOGIN,
    ROUTES.REGISTER,
    ROUTES.FORGOT_PASSWORD,
    ROUTES.RESET_PASSWORD,
    ROUTES.MFA_SETUP,
    ROUTES.MFA_VERIFY,
  ],
  WORKFLOWS: [
    ROUTES.WORKFLOWS,
    ROUTES.WORKFLOW_CREATE,
    ROUTES.WORKFLOW_DETAIL,
    ROUTES.WORKFLOW_EDIT,
    ROUTES.WORKFLOW_BUILDER,
    ROUTES.WORKFLOW_VERSIONS,
    ROUTES.WORKFLOW_TEMPLATES,
  ],
  EXECUTIONS: [
    ROUTES.EXECUTIONS,
    ROUTES.EXECUTION_DETAIL,
  ],
  CONNECTORS: [
    ROUTES.CONNECTORS,
    ROUTES.CONNECTOR_DETAIL,
    ROUTES.CONNECTOR_AUTHORIZE,
  ],
  DOCUMENTS: [
    ROUTES.DOCUMENTS,
    ROUTES.DOCUMENT_DETAIL,
    ROUTES.DOCUMENT_UPLOAD,
  ],
  ANALYTICS: [
    ROUTES.ANALYTICS,
    ROUTES.ANALYTICS_WORKFLOWS,
    ROUTES.ANALYTICS_EXECUTIONS,
    ROUTES.ANALYTICS_AI_USAGE,
    ROUTES.ANALYTICS_ERRORS,
  ],
  ORGANIZATION: [
    ROUTES.ORGANIZATION_SETTINGS,
    ROUTES.ORGANIZATION_MEMBERS,
    ROUTES.ORGANIZATION_ROLES,
    ROUTES.ORGANIZATION_API_KEYS,
    ROUTES.ORGANIZATION_BILLING,
    ROUTES.ORGANIZATION_AUDIT,
  ],
  USER: [
    ROUTES.USER_PROFILE,
    ROUTES.USER_SECURITY,
    ROUTES.USER_NOTIFICATIONS,
    ROUTES.USER_SESSIONS,
  ],
};

/**
 * Check if route is public (doesn't require authentication)
 */
export const isPublicRoute = (pathname) => {
  return ROUTE_GROUPS.AUTH.some((route) => {
    const regex = new RegExp(`^${route.replace(/:\w+/g, '[^/]+')}$`);
    return regex.test(pathname);
  });
};
