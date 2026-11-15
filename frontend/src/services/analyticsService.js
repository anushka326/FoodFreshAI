/**
 * FoodFresh AI — Impact Analytics Service
 * Handles API operations for Food-Waste Impact Analytics with strict user token auth.
 */

import { ENDPOINTS } from '../config/api.js';
import { getAuthHeaders, getCurrentUserId } from './storageUtils.js';
import { offlineSyncService } from './offlineSyncService.js';

function getAnalyticsCacheKey() {
  const uid = getCurrentUserId() || 'anonymous';
  return `foodfresh_analytics_cache_${uid}`;
}

export const analyticsService = {
  /**
   * Fetch current food-waste impact analytics for the authenticated user.
   */
  async getAnalytics() {
    try {
      const res = await fetch(ENDPOINTS.ANALYTICS, {
        headers: getAuthHeaders(),
      });
      if (res.status === 401) {
        return { has_activity: false, total_consumed: 0, total_wasted: 0, total_actions: 0 };
      }
      if (res.ok) {
        const data = await res.json();
        try {
          localStorage.setItem(getAnalyticsCacheKey(), JSON.stringify(data));
        } catch {}
        return data;
      }
    } catch (err) {
      console.warn('Backend analytics fetch failed (device may be offline):', err);
    }

    // Offline cache fallback
    try {
      const cachedRaw = localStorage.getItem(getAnalyticsCacheKey());
      if (cachedRaw) {
        const cached = JSON.parse(cachedRaw);
        return {
          ...cached,
          _isOfflineCached: true,
        };
      }
    } catch {}

    return {
      has_activity: false,
      total_consumed: 0,
      total_wasted: 0,
      total_actions: 0,
      waste_percentage: 0.0,
      food_saved_count: 0,
      food_saved_percentage: 0.0,
      monthly_trends: [],
      top_consumed_foods: [],
      top_wasted_foods: [],
      recent_actions: [],
      personalized_insights: [],
    };
  },

  /**
   * Record a food outcome (consumed or wasted).
   * Automatically queues offline when disconnected.
   */
  async recordAction({ foodName, action, pantryItemId = null, cultivar = null, reason = null }) {
    if (!foodName || !action) return null;

    if (!navigator.onLine) {
      console.log('[Analytics] Offline detected. Queuing impact action for reconnection sync.');
      offlineSyncService.enqueueAction('record_impact', {
        foodName,
        action,
        pantryItemId,
        cultivar,
        reason,
      });
      return {
        success: true,
        offlineQueued: true,
        data: {
          foodName,
          action,
          pantryItemId,
          createdAt: new Date().toISOString(),
        },
        message: 'Action saved offline. It will automatically sync when connection returns.',
      };
    }

    try {
      const res = await fetch(`${ENDPOINTS.ANALYTICS}/action`, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          food_name: foodName,
          action,
          pantry_item_id: pantryItemId,
          cultivar,
          reason,
        }),
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to record food action');
      }
      return await res.json();
    } catch (err) {
      console.warn('Failed to record food action on server, queuing offline:', err);
      offlineSyncService.enqueueAction('record_impact', {
        foodName,
        action,
        pantryItemId,
        cultivar,
        reason,
      });
      return {
        success: true,
        offlineQueued: true,
        data: {
          foodName,
          action,
          pantryItemId,
          createdAt: new Date().toISOString(),
        },
        message: 'Action saved offline. It will automatically sync when connection returns.',
      };
    }
  },

  /**
   * Delete an action log (undo).
   */
  async deleteAction(logId) {
    if (!logId) return false;
    try {
      const res = await fetch(`${ENDPOINTS.ANALYTICS}/action/${encodeURIComponent(logId)}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      return res.ok;
    } catch (err) {
      console.warn(`Failed to delete action ${logId}:`, err);
      return false;
    }
  },
};

export default analyticsService;

