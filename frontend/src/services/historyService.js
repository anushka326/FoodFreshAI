/**
 * Analysis History Service (User-Isolated Client-Side Store)
 * 
 * Manages user-specific food analysis history records.
 * Empty by default for every new user account.
 */

import { getCurrentUserId } from './storageUtils.js';
import { roadmapService } from './roadmapService.js';
import { FOOD_ASSETS } from '../assets/food/index.js';

function getStorageKey() {
  return `foodfresh_history_${getCurrentUserId()}`;
}

function getStoredHistory() {
  try {
    const raw = localStorage.getItem(getStorageKey());
    if (raw) {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    }
  } catch {
    // ignore
  }
  return [];
}

function saveStoredHistory(items) {
  try {
    localStorage.setItem(getStorageKey(), JSON.stringify(items));
  } catch {
    // ignore
  }
}

export const historyService = {
  /**
   * Get all past food analyses for current user
   */
  async getHistoryItems() {
    await new Promise((res) => setTimeout(res, 50));
    return getStoredHistory();
  },

  /**
   * Delete a record from history
   */
  async deleteHistoryItem(id) {
    await new Promise((res) => setTimeout(res, 50));
    const items = getStoredHistory().filter((item) => item.id !== id);
    saveStoredHistory(items);
    await roadmapService.removeFoodFromRoadmap(id);
    return true;
  },

  /**
   * Save a newly analyzed item into history and sync with Eat First roadmap
   */
  async saveToHistory(newItem) {
    await new Promise((res) => setTimeout(res, 80));
    const items = getStoredHistory();

    const record = {
      id: newItem.id || 'hist_' + Date.now(),
      foodName: newItem.foodName,
      cultivar: newItem.cultivar || `${newItem.foodName} • Fresh Harvest`,
      status: newItem.status || 'Fresh (Grade A)',
      statusCategory: newItem.statusCategory || 'fresh',
      qualityPeriod: newItem.qualityPeriod || '3–4 days left',
      storageEnvironment: newItem.storageSuggestion || newItem.storageEnvironment || 'Countertop Ambient',
      analyzedTime: 'Just now',
      qualityScore: newItem.qualityScore || 90,
      cellularIntegrity: newItem.cellularIntegrity || 'Intact',
      guidance:
        newItem.guidance ||
        (typeof newItem.culinaryGuidance === 'object'
          ? newItem.culinaryGuidance?.snacking
          : newItem.culinaryGuidance) ||
        'Store in optimal pantry conditions.',
      imageSrc: newItem.imageSrc || FOOD_ASSETS.cuttingBoardSourdough,
      imageCrop: 'object-cover',
      analyzedAt: newItem.analyzedAt || new Date().toISOString(),
    };

    // Prepend to user's history list
    items.unshift(record);
    saveStoredHistory(items);

    // Synchronize to Eat First roadmap dynamically
    await roadmapService.addFoodToRoadmap(record);

    return record;
  },

  /**
   * Reset store for current user to empty state
   */
  resetHistory() {
    saveStoredHistory([]);
    return [];
  },
};

export default historyService;
