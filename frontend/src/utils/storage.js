/**
 * Local Storage Utility
 * Handles all interactions with browser local storage
 */

import { STORAGE_KEYS } from '@constants';

/**
 * Get item from local storage
 * @param {string} key - Storage key
 * @param {*} defaultValue - Default value if key doesn't exist
 * @returns {*} Stored value or default value
 */
export const getStorageItem = (key, defaultValue = null) => {
  try {
    const item = window.localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error(`Error getting item from localStorage: ${key}`, error);
    return defaultValue;
  }
};

/**
 * Set item in local storage
 * @param {string} key - Storage key
 * @param {*} value - Value to store
 * @returns {boolean} Success status
 */
export const setStorageItem = (key, value) => {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.error(`Error setting item in localStorage: ${key}`, error);
    return false;
  }
};

/**
 * Remove item from local storage
 * @param {string} key - Storage key
 * @returns {boolean} Success status
 */
export const removeStorageItem = (key) => {
  try {
    window.localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error(`Error removing item from localStorage: ${key}`, error);
    return false;
  }
};

/**
 * Clear all items from local storage
 * @returns {boolean} Success status
 */
export const clearStorage = () => {
  try {
    window.localStorage.clear();
    return true;
  } catch (error) {
    console.error('Error clearing localStorage', error);
    return false;
  }
};

/**
 * Get access token from storage
 * @returns {string|null} Access token
 */
export const getAccessToken = () => {
  return getStorageItem(STORAGE_KEYS.accessToken);
};

/**
 * Set access token in storage
 * @param {string} token - Access token
 * @returns {boolean} Success status
 */
export const setAccessToken = (token) => {
  return setStorageItem(STORAGE_KEYS.accessToken, token);
};

/**
 * Get refresh token from storage
 * @returns {string|null} Refresh token
 */
export const getRefreshToken = () => {
  return getStorageItem(STORAGE_KEYS.refreshToken);
};

/**
 * Set refresh token in storage
 * @param {string} token - Refresh token
 * @returns {boolean} Success status
 */
export const setRefreshToken = (token) => {
  return setStorageItem(STORAGE_KEYS.refreshToken, token);
};

/**
 * Remove auth tokens from storage
 * @returns {boolean} Success status
 */
export const removeAuthTokens = () => {
  removeStorageItem(STORAGE_KEYS.accessToken);
  removeStorageItem(STORAGE_KEYS.refreshToken);
  return true;
};

/**
 * Get user data from storage
 * @returns {object|null} User data
 */
export const getUser = () => {
  return getStorageItem(STORAGE_KEYS.user);
};

/**
 * Set user data in storage
 * @param {object} user - User data
 * @returns {boolean} Success status
 */
export const setUser = (user) => {
  return setStorageItem(STORAGE_KEYS.user, user);
};

/**
 * Remove user data from storage
 * @returns {boolean} Success status
 */
export const removeUser = () => {
  return removeStorageItem(STORAGE_KEYS.user);
};

/**
 * Get organization data from storage
 * @returns {object|null} Organization data
 */
export const getOrganization = () => {
  return getStorageItem(STORAGE_KEYS.organization);
};

/**
 * Set organization data in storage
 * @param {object} organization - Organization data
 * @returns {boolean} Success status
 */
export const setOrganization = (organization) => {
  return setStorageItem(STORAGE_KEYS.organization, organization);
};

/**
 * Remove organization data from storage
 * @returns {boolean} Success status
 */
export const removeOrganization = () => {
  return removeStorageItem(STORAGE_KEYS.organization);
};

/**
 * Get theme from storage
 * @returns {string} Theme name
 */
export const getTheme = () => {
  return getStorageItem(STORAGE_KEYS.theme, 'light');
};

/**
 * Set theme in storage
 * @param {string} theme - Theme name
 * @returns {boolean} Success status
 */
export const setTheme = (theme) => {
  return setStorageItem(STORAGE_KEYS.theme, theme);
};
