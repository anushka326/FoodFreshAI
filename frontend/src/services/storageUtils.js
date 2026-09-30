/**
 * User storage utility to ensure complete data isolation between user accounts.
 */

const AUTH_STORAGE_KEY = 'foodfresh_ai_session';
const AUTH_TOKEN_KEY = 'foodfresh_ai_token';

export function getAuthToken() {
  try {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setAuthToken(token) {
  try {
    if (token) {
      localStorage.setItem(AUTH_TOKEN_KEY, token);
    } else {
      localStorage.removeItem(AUTH_TOKEN_KEY);
    }
  } catch {
    // ignore
  }
}

export function getAuthHeaders(extra = {}) {
  const token = getAuthToken();
  const headers = { ...extra };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export function getCurrentUserId() {
  try {
    const data = localStorage.getItem(AUTH_STORAGE_KEY);
    if (data) {
      const user = JSON.parse(data);
      if (user && user.id) return user.id;
    }
  } catch {
    // ignore
  }
  return null;
}

export function getStoredSessionUser() {
  try {
    const data = localStorage.getItem(AUTH_STORAGE_KEY);
    return data ? JSON.parse(data) : null;
  } catch {
    return null;
  }
}

export function setStoredSessionUser(user) {
  try {
    if (user) {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(AUTH_STORAGE_KEY);
    }
  } catch {
    // ignore
  }
}

export function clearAuthStorage() {
  setAuthToken(null);
  setStoredSessionUser(null);
}
