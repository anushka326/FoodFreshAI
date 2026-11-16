/**
 * Authentication Service — backend SQLite users + bearer session tokens
 * with seamless Offline / Live Demo Mode fallback for static GitHub Pages deployments.
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

const LOCAL_USERS_KEY = 'foodfresh_registered_users';

function getLocalRegisteredUsers() {
  try {
    const raw = localStorage.getItem(LOCAL_USERS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveLocalRegisteredUsers(users) {
  try {
    localStorage.setItem(LOCAL_USERS_KEY, JSON.stringify(users));
  } catch {}
}

/**
 * Seed realistic produce items for newly authenticated users if pantry is empty,
 * ensuring the live GitHub demo showcases the full gamified kitchen experience immediately.
 */
export function seedDefaultPantryIfEmpty(userId) {
  if (!userId) return;
  try {
    const key = `foodfresh_history_${userId}`;
    const existing = localStorage.getItem(key);
    if (!existing || JSON.parse(existing).length === 0) {
      const now = new Date();
      const starterItems = [
        {
          id: 'item_seed_tomato_' + Date.now(),
          analysisId: 'anls_seed_1',
          userId,
          foodName: 'Vine Tomatoes',
          cultivar: 'Vine-Ripened Roma • Fresh Harvest',
          status: 'Near Peak / Consume Soon',
          statusCategory: 'urgent',
          qualityScore: 58,
          storageEnvironment: 'Countertop Ambient',
          storageType: 'countertop',
          guidance: 'Consume within 24 hours. Ideal for Dal Tadka, fresh salsa, or tomato omelette.',
          imageSrc: 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&auto=format&fit=crop&q=80',
          analyzedAt: new Date(now.getTime() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          daysStored: 2,
          shelfLife: { minDays: 1, maxDays: 2, confidence: 0.94 },
          eatFirstPriority: {
            priorityScore: 92,
            urgencyTier: 'urgent',
            tier: 'urgent',
            daysRemaining: 1,
            urgencyText: 'Eat First — 1 Day Remaining',
            badgeClass: 'bg-error text-white',
            reason: 'Approaching peak ripeness. Prioritized to prevent spoilage.',
          },
        },
        {
          id: 'item_seed_broccoli_' + (Date.now() + 1),
          analysisId: 'anls_seed_2',
          userId,
          foodName: 'Organic Broccoli',
          cultivar: 'Calabrese Crown • Farm Fresh',
          status: 'Fresh & Crisp',
          statusCategory: 'fresh',
          qualityScore: 86,
          storageEnvironment: 'Crisper Drawer (4°C)',
          storageType: 'fridge',
          guidance: 'Keep loosely wrapped in damp towel. Perfect for vegetable stir fry or soup.',
          imageSrc: 'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=500&auto=format&fit=crop&q=80',
          analyzedAt: new Date(now.getTime() - 1 * 24 * 60 * 60 * 1000).toISOString(),
          daysStored: 1,
          shelfLife: { minDays: 3, maxDays: 5, confidence: 0.91 },
          eatFirstPriority: {
            priorityScore: 68,
            urgencyTier: 'moderate',
            tier: 'moderate',
            daysRemaining: 3,
            urgencyText: 'Use Soon — 3 Days Remaining',
            badgeClass: 'bg-amber-500 text-white',
            reason: 'In optimal condition. Recommended for this week’s meals.',
          },
        },
        {
          id: 'item_seed_apple_' + (Date.now() + 2),
          analysisId: 'anls_seed_3',
          userId,
          foodName: 'Royal Gala Apples',
          cultivar: 'Crisp Orchard Selection',
          status: 'Peak Freshness',
          statusCategory: 'fresh',
          qualityScore: 95,
          storageEnvironment: 'Cool Pantry (15°C)',
          storageType: 'countertop',
          guidance: 'Crisp, sweet, and firm. Store away from ethylene-sensitive leafy greens.',
          imageSrc: 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=500&auto=format&fit=crop&q=80',
          analyzedAt: now.toISOString(),
          daysStored: 0,
          shelfLife: { minDays: 7, maxDays: 10, confidence: 0.96 },
          eatFirstPriority: {
            priorityScore: 30,
            urgencyTier: 'fresh',
            tier: 'fresh',
            daysRemaining: 8,
            urgencyText: 'Fresh & Crisp — 8 Days Remaining',
            badgeClass: 'bg-emerald-600 text-white',
            reason: 'Excellent cellular integrity. Long shelf-life cushion.',
          },
        },
        {
          id: 'item_seed_mango_' + (Date.now() + 3),
          analysisId: 'anls_seed_4',
          userId,
          foodName: 'Alphonso Mango',
          cultivar: 'Ratnagiri Prime Harvest',
          status: 'Sweet & Aromatic',
          statusCategory: 'fresh',
          qualityScore: 91,
          storageEnvironment: 'Countertop Ambient',
          storageType: 'countertop',
          guidance: 'Aromatic and fragrant. Enjoy fresh or prepare mango lassi.',
          imageSrc: 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=500&auto=format&fit=crop&q=80',
          analyzedAt: now.toISOString(),
          daysStored: 0,
          shelfLife: { minDays: 4, maxDays: 6, confidence: 0.93 },
          eatFirstPriority: {
            priorityScore: 50,
            urgencyTier: 'moderate',
            tier: 'moderate',
            daysRemaining: 5,
            urgencyText: 'Ripe & Ready — 5 Days Remaining',
            badgeClass: 'bg-amber-500 text-white',
            reason: 'Rich fragrance and golden hue. Consume at peak sweetness.',
          },
        },
      ];
      localStorage.setItem(key, JSON.stringify(starterItems));
    }
  } catch (e) {
    console.warn('Could not seed initial pantry items:', e);
  }
}

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
  /**
   * Log in user: attempts live backend first, falls back gracefully to local demo session on static hosts.
   */
  async login(email, password, rememberMe = false) {
    if (!email || !email.trim() || !password) {
      throw new Error('Please enter both your email address and password.');
    }

    const cleanEmail = email.trim().toLowerCase();
    let backendAvailable = false;
    let res = null;

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3500);

      res = await fetch(ENDPOINTS.AUTH_LOGIN, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: cleanEmail, password }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      backendAvailable = true;
    } catch {
      // Backend unreachable or offline (e.g. GitHub Pages static deployment)
      backendAvailable = false;
    }

    if (backendAvailable && res) {
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(apiErrorMessage(data, 'Invalid email or password.'));
      }

      setAuthToken(data.token, rememberMe);
      setStoredSessionUser(data.user, rememberMe);
      seedDefaultPantryIfEmpty(data.user?.id);

      try {
        window.dispatchEvent(
          new CustomEvent('foodfresh_auth_state_changed', {
            detail: { authenticated: true, user: data.user },
          })
        );
      } catch {}

      return {
        success: true,
        token: data.token,
        user: data.user,
      };
    }

    // --- Seamless Local Demo Mode Authentication ---
    // Check if user was registered locally in this browser
    const registered = getLocalRegisteredUsers();
    const existing = registered.find((u) => u.email === cleanEmail);

    if (existing) {
      if (existing.password && existing.password !== password) {
        throw new Error('Incorrect password for this account. Please verify.');
      }
    }

    const displayName = cleanEmail.includes('anushka')
      ? 'Chef Anushka'
      : (existing?.fullName || (cleanEmail.split('@')[0].replace(/[._-]/g, ' ') || 'Kitchen Chef'));

    const formattedName = displayName.charAt(0).toUpperCase() + displayName.slice(1);
    const userId = existing?.id || (cleanEmail.includes('anushka') ? 'usr_chef_anushka' : 'usr_' + btoa(cleanEmail).replace(/[^a-zA-Z0-9]/g, '').slice(0, 10));

    const localUser = {
      id: userId,
      email: cleanEmail,
      fullName: formattedName,
      role: 'chef',
      avatar: existing?.avatar || 'fruit-apple',
      avatarUrl: existing?.avatarUrl || 'fruit-apple',
      level: 7,
      xp: 1420,
      isDemoSession: true,
      created_at: existing?.created_at || new Date().toISOString(),
    };

    const token = 'token_local_' + Date.now();
    setAuthToken(token, rememberMe);
    setStoredSessionUser(localUser, rememberMe);
    seedDefaultPantryIfEmpty(userId);

    try {
      window.dispatchEvent(
        new CustomEvent('foodfresh_auth_state_changed', {
          detail: { authenticated: true, user: localUser },
        })
      );
    } catch {}

    return {
      success: true,
      token,
      user: localUser,
      isDemoSession: true,
    };
  },

  /**
   * Register new user: attempts backend first, falls back to local storage registration.
   */
  async register({ fullName, email, password, rememberMe = false }) {
    if (!fullName || !fullName.trim()) {
      throw new Error('Please enter your full name or kitchen title.');
    }
    const cleanEmail = email.trim().toLowerCase();
    if (!cleanEmail) {
      throw new Error('Please enter your email address.');
    }
    if (!password) {
      throw new Error('Please create a password.');
    }
    if (password.length < 6) {
      throw new Error('Password must be at least 6 characters long.');
    }

    let backendAvailable = false;
    let res = null;

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3500);

      res = await fetch(ENDPOINTS.AUTH_REGISTER, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fullName: fullName.trim(),
          email: cleanEmail,
          password,
        }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      backendAvailable = true;
    } catch {
      backendAvailable = false;
    }

    if (backendAvailable && res) {
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(apiErrorMessage(data, 'Registration could not be completed. Please try again.'));
      }

      setAuthToken(data.token, rememberMe);
      setStoredSessionUser(data.user, rememberMe);
      seedDefaultPantryIfEmpty(data.user?.id);

      try {
        window.dispatchEvent(
          new CustomEvent('foodfresh_auth_state_changed', {
            detail: { authenticated: true, user: data.user },
          })
        );
      } catch {}

      return {
        success: true,
        token: data.token,
        user: data.user,
      };
    }

    // Local Demo registration fallback
    const registered = getLocalRegisteredUsers();
    if (registered.some((u) => u.email === cleanEmail)) {
      throw new Error('An account with this email address already exists. Please log in.');
    }

    const userId = 'usr_' + Date.now();
    const newUser = {
      id: userId,
      email: cleanEmail,
      fullName: fullName.trim(),
      role: 'chef',
      avatar: 'fruit-apple',
      avatarUrl: 'fruit-apple',
      level: 1,
      xp: 250,
      isDemoSession: true,
      created_at: new Date().toISOString(),
    };

    registered.push({ ...newUser, password });
    saveLocalRegisteredUsers(registered);

    const token = 'token_local_' + Date.now();
    setAuthToken(token, rememberMe);
    setStoredSessionUser(newUser, rememberMe);
    seedDefaultPantryIfEmpty(userId);

    try {
      window.dispatchEvent(
        new CustomEvent('foodfresh_auth_state_changed', {
          detail: { authenticated: true, user: newUser },
        })
      );
    } catch {}

    return {
      success: true,
      token,
      user: newUser,
      isDemoSession: true,
    };
  },

  isAuthenticated() {
    const session = getStoredSessionUser();
    const token = getAuthToken();
    return !!(session && session.id && token);
  },

  async validateSessionAsync() {
    const token = getAuthToken();
    if (!token) {
      clearAuthStorage();
      return false;
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      const res = await fetch(ENDPOINTS.AUTH_ME, {
        headers: getAuthHeaders(),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (res.status === 401) {
        clearAuthStorage();
        return false;
      }
      if (res.ok) {
        const data = await res.json();
        if (data?.user) {
          setStoredSessionUser(data.user);
          return true;
        }
      }
    } catch {
      // In offline / static demo conditions, preserve valid stored session
      return this.isAuthenticated();
    }
    return this.isAuthenticated();
  },

  getCurrentUserSync() {
    return getStoredSessionUser();
  },

  async getCurrentUser() {
    const cached = getStoredSessionUser();
    const token = getAuthToken();
    if (!token) return null;

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      const res = await fetch(ENDPOINTS.AUTH_ME, {
        headers: getAuthHeaders(),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (res.status === 401) {
        clearAuthStorage();
        return null;
      }
      if (res.ok) {
        const data = await res.json();
        if (data?.user) {
          setStoredSessionUser(data.user);
          return data.user;
        }
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
