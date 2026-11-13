/**
 * Analysis History Service — backend SQLite pantry with dynamic remaining quality.
 */

import { ENDPOINTS } from '../config/api.js';
import { getAuthHeaders } from './storageUtils.js';
import { roadmapService } from './roadmapService.js';
import { FOOD_ASSETS } from '../assets/food/index.js';

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
  async getHistoryItems() {
    try {
      const res = await fetch(ENDPOINTS.PANTRY_HISTORY, {
        headers: getAuthHeaders(),
      });
      if (res.status === 401) {
        return [];
      }
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data.items)) {
          const uid = data.items[0]?.userId;
          saveStoredHistory(uid, data.items);
          return data.items;
        }
      }
    } catch (e) {
      console.warn('Backend history fetch failed:', e);
    }
    return [];
  },

  async deleteHistoryItem(id) {
    try {
      const url = `${ENDPOINTS.PANTRY_HISTORY}/${encodeURIComponent(id)}`;
      await fetch(url, { method: 'DELETE', headers: getAuthHeaders() });
    } catch (e) {
      console.warn('Backend delete history failed:', e);
    }

    await roadmapService.removeFoodFromRoadmap(id);
    return true;
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
      console.warn('Backend save to history failed:', e);
      throw e;
    }

    await roadmapService.addFoodToRoadmap(record);
    return record;
  },

  resetHistory() {
    return this.clearAllHistory();
  },
};

export default historyService;
