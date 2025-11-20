import api from './api';
import { USER_ENDPOINTS } from '@/constants/apiEndpoints';

/**
 * User Service
 * Handles all user-related API calls
 */
const userService = {
  /**
   * Get current user profile
   * @returns {Promise}
   */
  getCurrentUser: () => {
    return api.get(USER_ENDPOINTS.ME);
  },

  /**
   * Update user profile
   * @param {Object} data - User data to update
   * @returns {Promise}
   */
  updateProfile: (data) => {
    return api.patch(USER_ENDPOINTS.PROFILE, data);
  },

  /**
   * Update user avatar
   * @param {File} file - Avatar image file
   * @returns {Promise}
   */
  updateAvatar: (file) => {
    const formData = new FormData();
    formData.append('avatar', file);
    return api.upload(USER_ENDPOINTS.AVATAR, formData);
  },

  /**
   * Delete user avatar
   * @returns {Promise}
   */
  deleteAvatar: () => {
    return api.delete(USER_ENDPOINTS.AVATAR);
  },

  /**
   * Change password
   * @param {Object} data - Password data (old_password, new_password)
   * @returns {Promise}
   */
  changePassword: (data) => {
    return api.post(USER_ENDPOINTS.CHANGE_PASSWORD, data);
  },

  /**
   * Get user settings
   * @returns {Promise}
   */
  getSettings: () => {
    return api.get(USER_ENDPOINTS.SETTINGS);
  },

  /**
   * Update user settings
   * @param {Object} settings - Settings to update
   * @returns {Promise}
   */
  updateSettings: (settings) => {
    return api.patch(USER_ENDPOINTS.SETTINGS, settings);
  },

  /**
   * Get user sessions
   * @returns {Promise}
   */
  getSessions: () => {
    return api.get(USER_ENDPOINTS.SESSIONS);
  },

  /**
   * Revoke user session
   * @param {string} sessionId - Session ID
   * @returns {Promise}
   */
  revokeSession: (sessionId) => {
    return api.delete(USER_ENDPOINTS.SESSION_DETAIL(sessionId));
  },

  /**
   * Get user activity log
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getActivityLog: (params = {}) => {
    return api.get(USER_ENDPOINTS.ACTIVITY, { params });
  },

  /**
   * Get user preferences
   * @returns {Promise}
   */
  getPreferences: () => {
    return api.get(USER_ENDPOINTS.PREFERENCES);
  },

  /**
   * Update user preferences
   * @param {Object} preferences - Preferences to update
   * @returns {Promise}
   */
  updatePreferences: (preferences) => {
    return api.patch(USER_ENDPOINTS.PREFERENCES, preferences);
  },

  /**
   * Enable two-factor authentication
   * @returns {Promise}
   */
  enable2FA: () => {
    return api.post(USER_ENDPOINTS.ENABLE_2FA);
  },

  /**
   * Disable two-factor authentication
   * @param {string} password - User password for verification
   * @returns {Promise}
   */
  disable2FA: (password) => {
    return api.post(USER_ENDPOINTS.DISABLE_2FA, { password });
  },

  /**
   * Verify 2FA code
   * @param {string} code - 2FA code
   * @returns {Promise}
   */
  verify2FA: (code) => {
    return api.post(USER_ENDPOINTS.VERIFY_2FA, { code });
  },

  /**
   * Get backup codes for 2FA
   * @returns {Promise}
   */
  getBackupCodes: () => {
    return api.get(USER_ENDPOINTS.BACKUP_CODES);
  },

  /**
   * Regenerate backup codes
   * @returns {Promise}
   */
  regenerateBackupCodes: () => {
    return api.post(USER_ENDPOINTS.REGENERATE_BACKUP_CODES);
  },
};

export default userService;
