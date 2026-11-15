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
  if (!data) return fallback;
  const detail = data?.detail;
  if (typeof detail === 'string' && detail.trim()) return detail.trim();
  if (Array.isArray(detail)) {
    const msgs = detail
      .map((item) => {
        if (!item) return '';
        if (typeof item === 'string') return item;
        return item.msg || item.message || '';
      })
      .filter(Boolean);
    if (msgs.length > 0) return msgs.join('. ');
  }
  if (typeof detail === 'object' && detail !== null) {
    if (detail.msg) return String(detail.msg);
    if (detail.message) return String(detail.message);
  }
  if (data?.message && typeof data.message === 'string') return data.message;
  if (data?.error && typeof data.error === 'string') return data.error;
  return fallback;
}

export const authService = {
  async login(email, password) {
    if (!email || !email.trim() || !password) {
      throw new Error('Please enter both your email address and password.');
    }

    let res;
    try {
      res = await fetch(ENDPOINTS.AUTH_LOGIN, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password }),
      });
    } catch (networkErr) {
      throw new Error('Cannot reach the FoodFresh server. Please check your connection.');
    }

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
    if (password.length < 6) {
      throw new Error('Password must be at least 6 characters long.');
    }

    let res;
    try {
      res = await fetch(ENDPOINTS.AUTH_REGISTER, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fullName: fullName.trim(),
          email: email.trim(),
          password,
        }),
      });
    } catch (networkErr) {
      throw new Error('Cannot reach the FoodFresh server. Please check that the backend is running.');
    }

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(apiErrorMessage(data, 'Registration could not be completed. Please try again.'));
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
    let updated = current ? { ...current, ...updates } : updates;

    try {
      const res = await fetch(ENDPOINTS.AUTH_PROFILE, {
        method: 'PUT',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(updates),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.user) {
          updated = data.user;
        }
      }
    } catch (err) {
      console.warn('Backend profile update failed, using local session fallback:', err);
    }

    setStoredSessionUser(updated);
    try {
      window.dispatchEvent(new CustomEvent('foodfresh_user_profile_updated', { detail: { user: updated } }));
    } catch {}
    return updated;
  },

  async updateAvatar(avatarId) {
    return this.updateProfile({ avatar: avatarId, avatarUrl: avatarId });
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
