/**
 * Eat First Roadmap Service (User-Isolated Client-Side Store)
 * 
 * Manages user-specific food priority scheduling and completion state.
 * Empty by default for every new user.
 */

import { getCurrentUserId } from './storageUtils.js';

function getStorageKey() {
  return `foodfresh_roadmap_${getCurrentUserId()}`;
}

function getStoredRoadmap() {
  try {
    const raw = localStorage.getItem(getStorageKey());
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        active: Array.isArray(parsed.active) ? parsed.active : [],
        completed: Array.isArray(parsed.completed) ? parsed.completed : [],
      };
    }
  } catch {
    // ignore
  }
  return { active: [], completed: [] };
}

function saveStoredRoadmap(data) {
  try {
    localStorage.setItem(getStorageKey(), JSON.stringify(data));
  } catch {
    // ignore
  }
}

function getFoodEmoji(name = '') {
  const lower = name.toLowerCase();
  if (lower.includes('apple')) return '🍎';
  if (lower.includes('tomato')) return '🍅';
  if (lower.includes('banana')) return '🍌';
  if (lower.includes('avocado')) return '🥑';
  if (lower.includes('bread') || lower.includes('sourdough')) return '🍞';
  if (lower.includes('spinach') || lower.includes('salad') || lower.includes('green')) return '🥬';
  if (lower.includes('orange') || lower.includes('citrus')) return '🍊';
  if (lower.includes('berry') || lower.includes('strawberr')) return '🍓';
  return '🥗';
}

export const roadmapService = {
  /**
   * Get active and completed roadmap items for current user
   */
  async getRoadmap() {
    await new Promise((res) => setTimeout(res, 50));
    const data = getStoredRoadmap();
    const total = data.active.length + data.completed.length;
    const completionRate = total > 0 ? Math.round((data.completed.length / total) * 100) : 0;
    return {
      active: [...data.active],
      completed: [...data.completed],
      total,
      completionRate,
    };
  },

  /**
   * Generate and add a roadmap item from a saved food analysis
   */
  async addFoodToRoadmap(foodItem) {
    const data = getStoredRoadmap();

    // Determine priority ranking based on freshness status and quality period
    let priorityRank = 3;
    let priorityTag = '🟢 Can Wait';
    let badgeType = 'fresh';
    let urgencyText = foodItem.qualityPeriod || 'Optimal fresh window';

    const statusCat = (foodItem.statusCategory || '').toLowerCase();
    const period = (foodItem.qualityPeriod || '').toLowerCase();
    const score = Number(foodItem.qualityScore) || 80;

    if (statusCat === 'attention' || period.includes('24h') || period.includes('1 day') || score < 60) {
      priorityRank = 1;
      priorityTag = '🥇 Eat First';
      badgeType = 'urgent';
      urgencyText = period.includes('24h') ? 'Consume within 24h' : 'Needs cook soon';
    } else if (statusCat === 'semi' || period.includes('2 day') || score < 75) {
      priorityRank = 2;
      priorityTag = '🥈 Eat Next';
      badgeType = 'warning';
      urgencyText = foodItem.qualityPeriod || 'Eat in 1–2 days';
    }

    const roadmapCard = {
      id: 'rd_' + (foodItem.id || Date.now()),
      historyId: foodItem.id,
      name: foodItem.foodName,
      priorityRank,
      priorityTag,
      badgeType,
      qualityWindow: foodItem.qualityPeriod || 'Active window',
      urgencyText,
      status: foodItem.status || 'Active Produce',
      description:
        foodItem.guidance ||
        (typeof foodItem.culinaryGuidance === 'object'
          ? foodItem.culinaryGuidance?.snacking
          : foodItem.culinaryGuidance) ||
        'Store in optimal pantry conditions and consume at peak freshness.',
      imageSrc: foodItem.imageSrc || '',
      fallbackEmoji: getFoodEmoji(foodItem.foodName),
    };

    // Remove existing item with same id if any, then insert and sort
    const existingActive = data.active.filter((item) => item.id !== roadmapCard.id && item.historyId !== foodItem.id);
    const updatedActive = [...existingActive, roadmapCard].sort((a, b) => a.priorityRank - b.priorityRank);

    data.active = updatedActive;
    saveStoredRoadmap(data);
    return this.getRoadmap();
  },

  /**
   * Mark an item as eaten / taken care of
   */
  async markAsEaten(itemId) {
    await new Promise((res) => setTimeout(res, 80));
    const data = getStoredRoadmap();
    const found = data.active.find((i) => i.id === itemId);
    if (found) {
      data.active = data.active.filter((i) => i.id !== itemId);
      data.completed.unshift({
        id: found.id,
        historyId: found.historyId,
        name: found.name,
        statusText: `Was: ${found.status} • Quality window: ${found.qualityWindow}`,
        eatenWhen: 'Eaten Today',
        imageSrc: found.imageSrc,
        fallbackEmoji: found.fallbackEmoji || getFoodEmoji(found.name),
      });
      saveStoredRoadmap(data);
    }
    return this.getRoadmap();
  },

  /**
   * Undo an eaten item and return to active roadmap
   */
  async undoEaten(itemId) {
    await new Promise((res) => setTimeout(res, 80));
    const data = getStoredRoadmap();
    const found = data.completed.find((i) => i.id === itemId);
    if (found) {
      data.completed = data.completed.filter((i) => i.id !== itemId);
      data.active.push({
        id: found.id,
        historyId: found.historyId,
        name: found.name,
        priorityRank: 2,
        priorityTag: '🥈 Eat Next',
        badgeType: 'warning',
        qualityWindow: 'Active plan',
        urgencyText: 'Active plan',
        status: 'Fresh Produce',
        description: 'Restored back onto your pantry eat priority plan.',
        imageSrc: found.imageSrc || '',
        fallbackEmoji: found.fallbackEmoji || getFoodEmoji(found.name),
      });
      data.active.sort((a, b) => a.priorityRank - b.priorityRank);
      saveStoredRoadmap(data);
    }
    return this.getRoadmap();
  },

  /**
   * Remove a food from roadmap (e.g. when deleted from history)
   */
  async removeFoodFromRoadmap(historyIdOrItemId) {
    const data = getStoredRoadmap();
    data.active = data.active.filter((i) => i.id !== historyIdOrItemId && i.historyId !== historyIdOrItemId);
    data.completed = data.completed.filter((i) => i.id !== historyIdOrItemId && i.historyId !== historyIdOrItemId);
    saveStoredRoadmap(data);
    return this.getRoadmap();
  },

  /**
   * Reset roadmap for current user to empty initial state
   */
  resetRoadmap() {
    saveStoredRoadmap({ active: [], completed: [] });
    return { active: [], completed: [], total: 0, completionRate: 0 };
  },
};

export default roadmapService;
