/**
 * FoodFresh AI - Frontend API Configuration
 * Supports environment overrides, direct local backend connection, and cloud endpoints.
 */

const DEFAULT_API_BASE = 'http://127.0.0.1:8000';

function resolveApiBaseUrl() {
  if (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL !== undefined) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  if (typeof window !== 'undefined') {
    try {
      const customUrl = localStorage.getItem('foodfresh_backend_url');
      if (customUrl && customUrl.trim()) {
        return customUrl.trim().replace(/\/+$/, '');
      }
    } catch {}

    // On local development, talk directly to the FastAPI server at 127.0.0.1:8000
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return 'http://127.0.0.1:8000';
    }

    // On GitHub Pages or static hosting without custom URL, use relative
    return '';
  }
  return DEFAULT_API_BASE;
}

export const API_BASE_URL = resolveApiBaseUrl();

export const ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/api/health`,
  AUTH_LOGIN: `${API_BASE_URL}/api/auth/login`,
  AUTH_REGISTER: `${API_BASE_URL}/api/auth/register`,
  AUTH_LOGOUT: `${API_BASE_URL}/api/auth/logout`,
  AUTH_ME: `${API_BASE_URL}/api/auth/me`,
  AUTH_PROFILE: `${API_BASE_URL}/api/auth/profile`,
  AUTH_AVATAR: `${API_BASE_URL}/api/auth/avatar`,
  FOOD_RECOGNITION: `${API_BASE_URL}/api/food-recognition/predict`,
  FRESHO_BUDDY_CHAT: `${API_BASE_URL}/api/fresho-buddy/chat`,
  FRESHO_BUDDY_CONVERSATIONS: `${API_BASE_URL}/api/fresho-buddy/conversations`,
  PANTRY_HISTORY: `${API_BASE_URL}/api/history`,
  RECIPE_RECOMMENDATIONS: `${API_BASE_URL}/api/recipes/recommendations`,
  NOTIFICATIONS: `${API_BASE_URL}/api/notifications`,
  ANALYTICS: `${API_BASE_URL}/api/analytics`,
  PACKAGED_FOOD_BARCODE: `${API_BASE_URL}/api/packaged-food/barcode-lookup`,
  PACKAGED_FOOD_SCAN_IMAGE: `${API_BASE_URL}/api/packaged-food/scan-image`,
  PACKAGED_FOOD_OCR: `${API_BASE_URL}/api/packaged-food/ocr`,
};
