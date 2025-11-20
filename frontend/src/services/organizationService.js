import api from './api';
import { ORGANIZATION_ENDPOINTS } from '@/constants/apiEndpoints';

/**
 * Organization Service
 * Handles all organization-related API calls
 */
const organizationService = {
  /**
   * Get current organization
   * @returns {Promise}
   */
  getOrganization: () => {
    return api.get(ORGANIZATION_ENDPOINTS.DETAIL);
  },

  /**
   * Update organization
   * @param {Object} data - Organization data
   * @returns {Promise}
   */
  updateOrganization: (data) => {
    return api.patch(ORGANIZATION_ENDPOINTS.DETAIL, data);
  },

  /**
   * Get organization members
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getMembers: (params = {}) => {
    return api.get(ORGANIZATION_ENDPOINTS.MEMBERS, { params });
  },

  /**
   * Get member by ID
   * @param {string} memberId - Member ID
   * @returns {Promise}
   */
  getMemberById: (memberId) => {
    return api.get(ORGANIZATION_ENDPOINTS.MEMBER_DETAIL(memberId));
  },

  /**
   * Invite member
   * @param {Object} inviteData - Invitation data (email, role)
   * @returns {Promise}
   */
  inviteMember: (inviteData) => {
    return api.post(ORGANIZATION_ENDPOINTS.INVITE, inviteData);
  },

  /**
   * Remove member
   * @param {string} memberId - Member ID
   * @returns {Promise}
   */
  removeMember: (memberId) => {
    return api.delete(ORGANIZATION_ENDPOINTS.MEMBER_DETAIL(memberId));
  },

  /**
   * Update member role
   * @param {string} memberId - Member ID
   * @param {string} role - New role
   * @returns {Promise}
   */
  updateMemberRole: (memberId, role) => {
    return api.patch(ORGANIZATION_ENDPOINTS.MEMBER_DETAIL(memberId), { role });
  },

  /**
   * Get available roles
   * @returns {Promise}
   */
  getRoles: () => {
    return api.get(ORGANIZATION_ENDPOINTS.ROLES);
  },

  /**
   * Create custom role
   * @param {Object} roleData - Role data
   * @returns {Promise}
   */
  createRole: (roleData) => {
    return api.post(ORGANIZATION_ENDPOINTS.ROLES, roleData);
  },

  /**
   * Update role permissions
   * @param {string} roleId - Role ID
   * @param {Object} permissions - Permissions
   * @returns {Promise}
   */
  updateRolePermissions: (roleId, permissions) => {
    return api.patch(ORGANIZATION_ENDPOINTS.ROLE_DETAIL(roleId), { permissions });
  },

  /**
   * Get pending invitations
   * @returns {Promise}
   */
  getInvitations: () => {
    return api.get(ORGANIZATION_ENDPOINTS.INVITATIONS);
  },

  /**
   * Cancel invitation
   * @param {string} invitationId - Invitation ID
   * @returns {Promise}
   */
  cancelInvitation: (invitationId) => {
    return api.delete(ORGANIZATION_ENDPOINTS.INVITATION_DETAIL(invitationId));
  },

  /**
   * Resend invitation
   * @param {string} invitationId - Invitation ID
   * @returns {Promise}
   */
  resendInvitation: (invitationId) => {
    return api.post(ORGANIZATION_ENDPOINTS.RESEND_INVITATION(invitationId));
  },

  /**
   * Get API keys
   * @returns {Promise}
   */
  getAPIKeys: () => {
    return api.get(ORGANIZATION_ENDPOINTS.API_KEYS);
  },

  /**
   * Create API key
   * @param {Object} data - API key data (name, permissions)
   * @returns {Promise}
   */
  createAPIKey: (data) => {
    return api.post(ORGANIZATION_ENDPOINTS.API_KEYS, data);
  },

  /**
   * Revoke API key
   * @param {string} keyId - API key ID
   * @returns {Promise}
   */
  revokeAPIKey: (keyId) => {
    return api.delete(ORGANIZATION_ENDPOINTS.API_KEY_DETAIL(keyId));
  },

  /**
   * Get organization settings
   * @returns {Promise}
   */
  getSettings: () => {
    return api.get(ORGANIZATION_ENDPOINTS.SETTINGS);
  },

  /**
   * Update organization settings
   * @param {Object} settings - Settings to update
   * @returns {Promise}
   */
  updateSettings: (settings) => {
    return api.patch(ORGANIZATION_ENDPOINTS.SETTINGS, settings);
  },

  /**
   * Get usage statistics
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getUsageStats: (params = {}) => {
    return api.get(ORGANIZATION_ENDPOINTS.USAGE, { params });
  },

  /**
   * Get billing information
   * @returns {Promise}
   */
  getBilling: () => {
    return api.get(ORGANIZATION_ENDPOINTS.BILLING);
  },
};

export default organizationService;
