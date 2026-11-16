/**
 * FoodFresh AI - Recipe Service
 * Handles all API calls for recipe recommendations with graceful offline fallback.
 */

import { API_BASE_URL } from '../config/api.js';
import { getAuthHeaders } from './storageUtils.js';
import { buildFallbackRecommendations, FALLBACK_RECIPES } from './recipeFallbackData.js';

export const recipeService = {
  /**
   * GET /api/recipes/recommendations
   * Returns full recommendations response, falling back to rich curated database when offline.
   */
  async getRecommendations() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3500);

      const response = await fetch(`${API_BASE_URL}/api/recipes/recommendations`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (response.status === 401) {
        return null;
      }

      if (response.ok) {
        return await response.json();
      }
    } catch (err) {
      console.warn('Backend recipe API unavailable, using offline Indian & zero-waste catalog:', err);
    }

    // Return rich offline fallback
    return {
      success: true,
      recommendations: buildFallbackRecommendations(),
      isOfflineFallback: true,
    };
  },

  /**
   * GET /api/recipes/recommendations/{id}
   */
  async getRecipeById(id) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3500);

      const response = await fetch(`${API_BASE_URL}/api/recipes/recommendations/${id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (response.status === 401) {
        return null;
      }

      if (response.ok) {
        return await response.json();
      }
    } catch (err) {
      console.warn('Backend recipe detail API unavailable:', err);
    }

    const matched = FALLBACK_RECIPES.find((r) => r.id === id) || FALLBACK_RECIPES[0];
    return {
      success: true,
      recipe: matched,
      isOfflineFallback: true,
    };
  },
};

export default recipeService;
