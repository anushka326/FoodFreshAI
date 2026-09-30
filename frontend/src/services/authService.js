/**
 * Authentication Service — backend SQLite users + bearer session tokens.
 */

import { ENDPOINTS } from '../config/api.js';
import {
  clearAuthStorage,
  getAuthHeaders,
  getAuthToken,
  getStoredSessionUser,
  setAuthToken,
  setStoredSessionUser,
} from './storageUtils.js';

function apiErrorMessage(data, fallback) {
  const detail = data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || item.message || String(item)).join(' ');
  }
  return fallback;
}

export const authService = {
  async login(email, password) {
    if (!email || !email.trim() || !password) {
      throw new Error('Please enter both your email address and password.');
    }

    const res = await fetch(ENDPOINTS.AUTH_LOGIN, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.trim(), password }),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(apiErrorMessage(data, 'Invalid email or password.'));
    }

    setAuthToken(data.token);
    setStoredSessionUser(data.user);

    return {
      success: true,
      token: data.token,
      user: data.user,
    };
  },

  async register({ fullName, email, password }) {
    if (!fullName || !fullName.trim()) {
      throw new Error('Please enter your full name or kitchen title.');
    }
    if (!email || !email.trim()) {
      throw new Error('Please enter your email address.');
    }
    if (!password) {
      throw new Error('Please create a password.');
    }

    const res = await fetch(ENDPOINTS.AUTH_REGISTER, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fullName: fullName.trim(),
        email: email.trim(),
        password,
      }),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(apiErrorMessage(data, 'Registration failed.'));
    }

    setAuthToken(data.token);
    setStoredSessionUser(data.user);

    return {
      success: true,
      token: data.token,
      user: data.user,
    };
  },

  isAuthenticated() {
    const session = getStoredSessionUser();
    const token = getAuthToken();
    return !!(session && session.id && token);
  },

  getCurrentUserSync() {
    return getStoredSessionUser();
  },

  async getCurrentUser() {
    const cached = getStoredSessionUser();
    const token = getAuthToken();
    if (!token) {
      return null;
    }
    try {
      const res = await fetch(ENDPOINTS.AUTH_ME, { headers: getAuthHeaders() });
      if (!res.ok) {
        clearAuthStorage();
        return null;
      }
      const data = await res.json();
      if (data.user) {
        setStoredSessionUser(data.user);
        return data.user;
      }
    } catch {
      return cached;
    }
    return cached;
  },

  async updateProfile(updates) {
    const current = getStoredSessionUser();
    if (!current) {
      return null;
    }
    const updated = { ...current, ...updates };
    setStoredSessionUser(updated);
    return updated;
  },

  async logout() {
    try {
      await fetch(ENDPOINTS.AUTH_LOGOUT, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
    } catch {
      // ignore network errors on logout
    }
    clearAuthStorage();
    return true;
  },

  async changePassword() {
    return { success: true };
  },

  async deleteAccount() {
    clearAuthStorage();
    return { success: true };
  },
};

export default authService;
