import api from './api';
import { NOTIFICATION_ENDPOINTS } from '@/constants/apiEndpoints';

/**
 * Notification Service
 * Handles all notification-related API calls
 */
const notificationService = {
  /**
   * Get all notifications
   * @param {Object} params - Query parameters
   * @returns {Promise}
   */
  getNotifications: (params = {}) => {
    return api.get(NOTIFICATION_ENDPOINTS.LIST, { params });
  },

  /**
   * Get unread notifications count
   * @returns {Promise}
   */
  getUnreadCount: () => {
    return api.get(NOTIFICATION_ENDPOINTS.UNREAD_COUNT);
  },

  /**
   * Mark notification as read
   * @param {string} id - Notification ID
   * @returns {Promise}
   */
  markAsRead: (id) => {
    return api.post(NOTIFICATION_ENDPOINTS.MARK_READ(id));
  },

  /**
   * Mark all notifications as read
   * @returns {Promise}
   */
  markAllAsRead: () => {
    return api.post(NOTIFICATION_ENDPOINTS.MARK_ALL_READ);
  },

  /**
   * Delete notification
   * @param {string} id - Notification ID
   * @returns {Promise}
   */
  deleteNotification: (id) => {
    return api.delete(NOTIFICATION_ENDPOINTS.DETAIL(id));
  },

  /**
   * Delete all read notifications
   * @returns {Promise}
   */
  deleteAllRead: () => {
    return api.delete(NOTIFICATION_ENDPOINTS.DELETE_ALL_READ);
  },

  /**
   * Get notification preferences
   * @returns {Promise}
   */
  getPreferences: () => {
    return api.get(NOTIFICATION_ENDPOINTS.PREFERENCES);
  },

  /**
   * Update notification preferences
   * @param {Object} preferences - Preferences to update
   * @returns {Promise}
   */
  updatePreferences: (preferences) => {
    return api.patch(NOTIFICATION_ENDPOINTS.PREFERENCES, preferences);
  },

  /**
   * Test notification channel
   * @param {string} channel - Channel to test (email, slack, etc.)
   * @returns {Promise}
   */
  testChannel: (channel) => {
    return api.post(NOTIFICATION_ENDPOINTS.TEST, { channel });
  },
};

export default notificationService;
