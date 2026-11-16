/**
 * Analysis History Service — backend SQLite pantry with dynamic remaining quality.
 */

import { ENDPOINTS } from '../config/api.js';
import { getAuthHeaders, getCurrentUserId } from './storageUtils.js';
import { roadmapService } from './roadmapService.js';
import { offlineSyncService } from './offlineSyncService.js';
import { FOOD_ASSETS } from '../assets/food/index.js';
import { seedDefaultPantryIfEmpty } from './authService.js';

function getStorageKey(userId) {
  return `foodfresh_history_${userId || 'unknown'}`;
}

function getStoredHistory(userId) {
  try {
    const raw = localStorage.getItem(getStorageKey(userId));
    if (raw) {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    }
  } catch {
    // ignore
  }
  return [];
}

function saveStoredHistory(userId, items) {
  try {
    localStorage.setItem(getStorageKey(userId), JSON.stringify(items));
  } catch {
    // ignore
  }
}

export const historyService = {
  /**
   * Fetch complete history bundle: active pantry, archived/removed produce, and activity logs.
   */
  async getHistoryData() {
    const currentUid = getCurrentUserId();
    try {
      const res = await fetch(ENDPOINTS.PANTRY_HISTORY, {
        headers: getAuthHeaders(),
      });
      if (res.status === 401) {
        return { items: [], archivedItems: [], activityLogs: [], count: 0, archivedCount: 0, totalTracked: 0 };
      }
      if (res.ok) {
        const data = await res.json();
        const items = Array.isArray(data.items) ? data.items : [];
        const archivedItems = Array.isArray(data.archived_items) ? data.archived_items : [];
        const activityLogs = Array.isArray(data.activity_logs) ? data.activity_logs : [];
        if (items.length > 0) {
          const uid = items[0]?.userId || currentUid;
          saveStoredHistory(uid, items);
        }
        return {
          items,
          archivedItems,
          activityLogs,
          count: items.length,
          archivedCount: archivedItems.length,
          totalTracked: data.total_tracked || (items.length + archivedItems.length),
        };
      }
    } catch (e) {
      console.warn('Backend history fetch failed (device may be offline):', e);
    }

    // Offline fallback: return cached active items
    if (currentUid) {
      let cached = getStoredHistory(currentUid);
      if (!cached || cached.length === 0) {
        seedDefaultPantryIfEmpty(currentUid);
        cached = getStoredHistory(currentUid);
      }
      if (cached && cached.length > 0) {
        const cachedItems = cached.map((item) => ({
          ...item,
          _isOfflineCached: true,
        }));
        return {
          items: cachedItems,
          archivedItems: [],
          activityLogs: [],
          count: cachedItems.length,
          archivedCount: 0,
          totalTracked: cachedItems.length,
        };
      }
    }
    return { items: [], archivedItems: [], activityLogs: [], count: 0, archivedCount: 0, totalTracked: 0 };
  },

  async getHistoryItems() {
    const data = await this.getHistoryData();
    return data.items;
  },

  async getArchivedItems() {
    try {
      const res = await fetch(`${ENDPOINTS.PANTRY_HISTORY}/archived`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        return Array.isArray(data.items) ? data.items : [];
      }
    } catch (e) {
      console.warn('Failed to fetch archived history:', e);
    }
    return [];
  },

  async getActivityLogs() {
    try {
      const res = await fetch(`${ENDPOINTS.PANTRY_HISTORY}/activity-logs`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        return Array.isArray(data.logs) ? data.logs : [];
      }
    } catch (e) {
      console.warn('Failed to fetch activity logs:', e);
    }
    return [];
  },

  async deleteHistoryItem(id, options = {}) {
    const currentUid = getCurrentUserId();
    const action = typeof options === 'string' ? options : (options?.action || 'removed');
    const reason = typeof options === 'object' ? (options?.reason || '') : '';

    if (!navigator.onLine) {
      offlineSyncService.enqueueAction('delete_pantry', { id, action, reason });

      if (currentUid) {
        const cached = getStoredHistory(currentUid);
        saveStoredHistory(currentUid, cached.filter((item) => item.id !== id));
      }
      await roadmapService.removeFoodFromRoadmap(id);
      return true;
    }

    try {
      const query = new URLSearchParams({ action, reason }).toString();
      const url = `${ENDPOINTS.PANTRY_HISTORY}/${encodeURIComponent(id)}?${query}`;
      await fetch(url, { method: 'DELETE', headers: getAuthHeaders() });
    } catch (e) {
      console.warn('Backend delete history failed, queuing offline:', e);
      offlineSyncService.enqueueAction('delete_pantry', { id, action, reason });
    }

    if (currentUid) {
      const cached = getStoredHistory(currentUid);
      saveStoredHistory(currentUid, cached.filter((item) => item.id !== id));
    }
    await roadmapService.removeFoodFromRoadmap(id);
    return true;
  },

  async restoreHistoryItem(id) {
    if (!id) return false;
    try {
      const url = `${ENDPOINTS.PANTRY_HISTORY}/${encodeURIComponent(id)}/restore`;
      const res = await fetch(url, { method: 'POST', headers: getAuthHeaders() });
      return res.ok;
    } catch (e) {
      console.warn('Backend restore history failed:', e);
      return false;
    }
  },

  async permanentlyDeleteHistoryItem(id) {
    if (!id) return false;
    try {
      const url = `${ENDPOINTS.PANTRY_HISTORY}/${encodeURIComponent(id)}/permanent`;
      const res = await fetch(url, { method: 'DELETE', headers: getAuthHeaders() });
      return res.ok;
    } catch (e) {
      console.warn('Backend permanent delete failed:', e);
      return false;
    }
  },

  async clearAllHistory() {
    try {
      await fetch(ENDPOINTS.PANTRY_HISTORY, { method: 'DELETE', headers: getAuthHeaders() });
    } catch (e) {
      console.warn('Backend clear history failed:', e);
    }
    return [];
  },

  async saveToHistory(newItem) {
    if (!newItem || newItem.source === 'none' || (!newItem.foodName && !newItem.detectedFood)) {
      return null;
    }

    const foodName = newItem.detectedFood || newItem.foodName;
    const freshness = newItem.freshness || {};
    const ef = newItem.eatFirstPriority;

    const record = {
      id: newItem.id || 'hist_' + Date.now(),
      analysisId: newItem.id || 'anls_' + Date.now(),
      foodName,
      cultivar: newItem.cultivar || `${foodName} • Fresh Harvest`,
      status: newItem.status || freshness.label || 'Fresh',
      statusCategory: newItem.statusCategory || 'fresh',
      qualityScore: newItem.qualityScore || Math.round((newItem.recognitionConfidence || 0.9) * 100),
      storageEnvironment: newItem.storageSuggestion || newItem.storageEnvironment || 'Countertop Ambient',
      storageType: newItem.storageType || newItem.storageContext?.storage || 'countertop',
      guidance:
        newItem.guidance ||
        (typeof newItem.culinaryGuidance === 'object'
          ? newItem.culinaryGuidance?.snacking
          : newItem.culinaryGuidance) ||
        'Store in optimal pantry conditions.',
      imageSrc: newItem.imageSrc || FOOD_ASSETS.cuttingBoardSourdough,
      analyzedAt: newItem.analyzedAt || new Date().toISOString(),
      shelfLife: newItem.shelfLife || null,
      freshness: newItem.freshness || null,
      freshnessState: freshness.label || null,
      freshnessConfidence: freshness.confidence ?? freshness.score ?? null,
      modelVersions: newItem.modelVersions || null,
      eatFirstPriority: ef,
      eatFirstScore: typeof ef === 'object' && ef ? ef.score : newItem.eatFirstScore,
      eatFirstReason: typeof ef === 'object' && ef ? ef.reason : newItem.eatFirstReason,
    };

    try {
      const res = await fetch(ENDPOINTS.PANTRY_HISTORY, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ item: record }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.item) {
          Object.assign(record, data.item);
        }
      } else if (res.status === 401) {
        throw new Error('Please sign in to save items to your pantry history.');
      }
    } catch (e) {
      if (e.message && e.message.includes('sign in')) {
        throw e;
      }
      console.warn('Backend save to history failed, using local offline storage:', e);
      if (currentUid) {
        const cached = getStoredHistory(currentUid);
        saveStoredHistory(currentUid, [record, ...cached.filter((it) => it.id !== record.id)]);
      }
    }

    await roadmapService.addFoodToRoadmap(record);
    return record;
  },

  resetHistory() {
    return this.clearAllHistory();
  },
};

export default historyService;
