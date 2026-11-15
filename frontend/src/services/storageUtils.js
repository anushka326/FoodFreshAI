/**
 * User storage utility to ensure complete data isolation between user accounts
 * and secure credential-based session lifecycle management.
 */

const AUTH_STORAGE_KEY = 'foodfresh_ai_session';
const AUTH_TOKEN_KEY = 'foodfresh_ai_token';
const AUTH_TIMESTAMP_KEY = 'foodfresh_ai_auth_ts';
const AUTH_PERSIST_KEY = 'foodfresh_ai_auth_persist';

// Maximum session lifetimes
const SESSION_MAX_AGE_PERSISTENT_MS = 24 * 60 * 60 * 1000; // 24 hours
const SESSION_MAX_AGE_TRANSIENT_MS = 8 * 60 * 60 * 1000;   // 8 hours

function isSessionExpired() {
  try {
    const tsStr = sessionStorage.getItem(AUTH_TIMESTAMP_KEY) || localStorage.getItem(AUTH_TIMESTAMP_KEY);
    if (!tsStr) return false;
    const ts = parseInt(tsStr, 10);
    if (isNaN(ts)) return true;
    const isPersistent = localStorage.getItem(AUTH_PERSIST_KEY) === 'true';
    const maxAge = isPersistent ? SESSION_MAX_AGE_PERSISTENT_MS : SESSION_MAX_AGE_TRANSIENT_MS;
    if (Date.now() - ts > maxAge) {
      return true;
    }
  } catch {
    return true;
  }
  return false;
}

export function getAuthToken() {
  try {
    if (isSessionExpired()) {
      clearAuthStorage();
      return null;
    }
    // Prefer sessionStorage (active browser session) over localStorage
    const sessionToken = sessionStorage.getItem(AUTH_TOKEN_KEY);
    if (sessionToken) return sessionToken;
    return localStorage.getItem(AUTH_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setAuthToken(token, persist = false) {
  try {
    if (token) {
      const now = Date.now().toString();
      if (persist) {
        localStorage.setItem(AUTH_TOKEN_KEY, token);
        localStorage.setItem(AUTH_TIMESTAMP_KEY, now);
        localStorage.setItem(AUTH_PERSIST_KEY, 'true');
        sessionStorage.removeItem(AUTH_TOKEN_KEY);
        sessionStorage.removeItem(AUTH_TIMESTAMP_KEY);
      } else {
        sessionStorage.setItem(AUTH_TOKEN_KEY, token);
        sessionStorage.setItem(AUTH_TIMESTAMP_KEY, now);
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem(AUTH_TIMESTAMP_KEY);
        localStorage.removeItem(AUTH_PERSIST_KEY);
      }
    } else {
      localStorage.removeItem(AUTH_TOKEN_KEY);
      localStorage.removeItem(AUTH_TIMESTAMP_KEY);
      localStorage.removeItem(AUTH_PERSIST_KEY);
      sessionStorage.removeItem(AUTH_TOKEN_KEY);
      sessionStorage.removeItem(AUTH_TIMESTAMP_KEY);
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
    const user = getStoredSessionUser();
    if (user && user.id) return user.id;
  } catch {
    // ignore
  }
  return null;
}

export function getStoredSessionUser() {
  try {
    if (isSessionExpired()) {
      clearAuthStorage();
      return null;
    }
    const sessionData = sessionStorage.getItem(AUTH_STORAGE_KEY);
    if (sessionData) {
      return JSON.parse(sessionData);
    }
    const localData = localStorage.getItem(AUTH_STORAGE_KEY);
    if (localData) {
      return JSON.parse(localData);
    }
    return null;
  } catch {
    return null;
  }
}

export function setStoredSessionUser(user, persist = false) {
  try {
    if (user) {
      const userStr = JSON.stringify(user);
      if (persist) {
        localStorage.setItem(AUTH_STORAGE_KEY, userStr);
        sessionStorage.removeItem(AUTH_STORAGE_KEY);
      } else {
        sessionStorage.setItem(AUTH_STORAGE_KEY, userStr);
        localStorage.removeItem(AUTH_STORAGE_KEY);
      }
    } else {
      localStorage.removeItem(AUTH_STORAGE_KEY);
      sessionStorage.removeItem(AUTH_STORAGE_KEY);
    }
  } catch {
    // ignore
  }
}

export function clearAuthStorage() {
  try {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_TIMESTAMP_KEY);
    localStorage.removeItem(AUTH_PERSIST_KEY);
    sessionStorage.removeItem(AUTH_STORAGE_KEY);
    sessionStorage.removeItem(AUTH_TOKEN_KEY);
    sessionStorage.removeItem(AUTH_TIMESTAMP_KEY);
    try {
      window.dispatchEvent(new CustomEvent('foodfresh_auth_state_changed', { detail: { authenticated: false } }));
    } catch {}
  } catch {
    // ignore
  }
}
