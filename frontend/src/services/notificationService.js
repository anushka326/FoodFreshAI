/**
 * FoodFresh AI — Notification Service
 * Handles API operations for Smart Notifications & Expiry Alerts with user token auth.
 */

import { ENDPOINTS } from '../config/api.js';
import { getAuthHeaders } from './storageUtils.js';

export const notificationService = {
  /**
   * Fetch all active pantry notifications for the authenticated user.
   */
  async getNotifications() {
    try {
      const res = await fetch(ENDPOINTS.NOTIFICATIONS, {
        headers: getAuthHeaders(),
      });
      if (res.status === 401) {
        return { notifications: [], unread_count: 0, total_count: 0, summary: {} };
      }
      if (!res.ok) {
        throw new Error(`Failed to fetch notifications: ${res.statusText}`);
      }
      const data = await res.json();
      return {
        notifications: Array.isArray(data.notifications) ? data.notifications : [],
        unread_count: Number(data.unread_count) || 0,
        total_count: Number(data.total_count) || 0,
        summary: data.summary || {},
      };
    } catch (err) {
      console.warn('Backend notifications fetch failed:', err);
      return { notifications: [], unread_count: 0, total_count: 0, summary: {} };
    }
  },

  /**
   * Mark a specific notification as read.
   */
  async markAsRead(notificationId) {
    if (!notificationId) return false;
    try {
      const url = `${ENDPOINTS.NOTIFICATIONS}/${encodeURIComponent(notificationId)}/read`;
      const res = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      });
      return res.ok;
    } catch (err) {
      console.warn(`Failed to mark notification ${notificationId} as read:`, err);
      return false;
    }
  },

  /**
   * Mark a specific notification as unread.
   */
  async markAsUnread(notificationId) {
    if (!notificationId) return false;
    try {
      const url = `${ENDPOINTS.NOTIFICATIONS}/${encodeURIComponent(notificationId)}/unread`;
      const res = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      });
      return res.ok;
    } catch (err) {
      console.warn(`Failed to mark notification ${notificationId} as unread:`, err);
      return false;
    }
  },

  /**
   * Mark all active notifications as read.
   */
  async markAllAsRead(notificationIds = null) {
    try {
      const url = `${ENDPOINTS.NOTIFICATIONS}/read-all`;
      const res = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ notification_ids: notificationIds }),
      });
      return res.ok;
    } catch (err) {
      console.warn('Failed to mark all notifications as read:', err);
      return false;
    }
  },
};

export default notificationService;

