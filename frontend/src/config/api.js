/**
 * FoodFresh AI - Frontend API Configuration
 * Supports environment overrides and falls back to proxy / direct FastAPI backend.
 */

const DEFAULT_API_BASE = 'http://localhost:8000';

export const API_BASE_URL = 
  import.meta.env.VITE_API_BASE_URL !== undefined
    ? import.meta.env.VITE_API_BASE_URL
    : (typeof window !== 'undefined' && (window.location.port === '3000' || window.location.port === '5173')
        ? '' 
        : DEFAULT_API_BASE);

export const ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/api/health`,
  AUTH_LOGIN: `${API_BASE_URL}/api/auth/login`,
  AUTH_REGISTER: `${API_BASE_URL}/api/auth/register`,
  AUTH_LOGOUT: `${API_BASE_URL}/api/auth/logout`,
  AUTH_ME: `${API_BASE_URL}/api/auth/me`,
  FOOD_RECOGNITION: `${API_BASE_URL}/api/food-recognition/predict`,
  FRESHO_BUDDY_CHAT: `${API_BASE_URL}/api/fresho-buddy/chat`,
  FRESHO_BUDDY_CONVERSATIONS: `${API_BASE_URL}/api/fresho-buddy/conversations`,
  PANTRY_HISTORY: `${API_BASE_URL}/api/history`,
};
