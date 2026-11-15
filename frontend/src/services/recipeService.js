/**
 * FoodFresh AI - Recipe Service
 * Handles all API calls for recipe recommendations.
 */

import { API_BASE_URL } from '../config/api.js';
import { getAuthHeaders } from './storageUtils.js';

export const recipeService = {
  /**
   * GET /api/recipes/recommendations
   * Returns the full recommendations response or throws on error.
   * Returns null on 401 (unauthenticated).
   */
  async getRecommendations() {
    const response = await fetch(`${API_BASE_URL}/api/recipes/recommendations`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });

    if (response.status === 401) {
      return null;
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }

    return response.json();
  },

  /**
   * GET /api/recipes/recommendations/{id}
   * Returns a single recipe by ID or throws on error.
   * Returns null on 401 (unauthenticated).
   */
  async getRecipeById(id) {
    const response = await fetch(`${API_BASE_URL}/api/recipes/recommendations/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });

    if (response.status === 401) {
      return null;
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }

    return response.json();
  },
};

export default recipeService;
