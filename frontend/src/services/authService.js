/**
 * Authentication Service
 * Handles all authentication-related API calls
 */

import { post, get } from './api';
import { AUTH_ENDPOINTS } from '@constants';
import { setAccessToken, setRefreshToken, setUser, removeAuthTokens, removeUser } from '@utils';

/**
 * Login user
 * @param {object} credentials - Login credentials
 * @returns {Promise} Response promise
 */
export const login = async (credentials) => {
  const response = await post(AUTH_ENDPOINTS.login, credentials);
  const { access, refresh, user } = response.data;

  // Store tokens and user data
  setAccessToken(access);
  setRefreshToken(refresh);
  setUser(user);

  return response.data;
};

/**
 * Register new user
 * @param {object} userData - User registration data
 * @returns {Promise} Response promise
 */
export const register = async (userData) => {
  const response = await post(AUTH_ENDPOINTS.register, userData);
  return response.data;
};

/**
 * Logout user
 * @returns {Promise} Response promise
 */
export const logout = async () => {
  try {
    await post(AUTH_ENDPOINTS.logout);
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Always clear local storage
    removeAuthTokens();
    removeUser();
  }
};

/**
 * Request password reset
 * @param {string} email - User email
 * @returns {Promise} Response promise
 */
export const requestPasswordReset = async (email) => {
  const response = await post(AUTH_ENDPOINTS.passwordReset, { email });
  return response.data;
};

/**
 * Confirm password reset
 * @param {object} data - Reset data (token, new password)
 * @returns {Promise} Response promise
 */
export const confirmPasswordReset = async (data) => {
  const response = await post(AUTH_ENDPOINTS.passwordResetConfirm, data);
  return response.data;
};

/**
 * Get current user
 * @returns {Promise} Response promise
 */
export const getCurrentUser = async () => {
  const response = await get(AUTH_ENDPOINTS.me);
  setUser(response.data);
  return response.data;
};

/**
 * Setup MFA
 * @returns {Promise} Response promise with QR code
 */
export const setupMFA = async () => {
  const response = await post(AUTH_ENDPOINTS.mfaSetup);
  return response.data;
};

/**
 * Verify MFA
 * @param {string} code - MFA code
 * @returns {Promise} Response promise
 */
export const verifyMFA = async (code) => {
  const response = await post(AUTH_ENDPOINTS.mfaVerify, { code });
  return response.data;
};

/**
 * Disable MFA
 * @param {string} password - User password for confirmation
 * @returns {Promise} Response promise
 */
export const disableMFA = async (password) => {
  const response = await post(AUTH_ENDPOINTS.mfaDisable, { password });
  return response.data;
};

export default {
  login,
  register,
  logout,
  requestPasswordReset,
  confirmPasswordReset,
  getCurrentUser,
  setupMFA,
  verifyMFA,
  disableMFA,
};
