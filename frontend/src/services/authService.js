/**
 * Authentication Service Interface (Client-Side State)
 * 
 * Prepares frontend components for future FastAPI backend integration.
 * In production, this will communicate with:
 * POST /api/v1/auth/login
 * POST /api/v1/auth/register
 * POST /api/v1/auth/logout
 * GET  /api/v1/auth/me
 */

const AUTH_STORAGE_KEY = 'foodfresh_ai_session';
const USERS_REGISTRY_KEY = 'foodfresh_ai_users';

function getStoredUsers() {
  try {
    const data = localStorage.getItem(USERS_REGISTRY_KEY);
    return data ? JSON.parse(data) : {};
  } catch {
    return {};
  }
}

function saveUserToRegistry(user) {
  try {
    const users = getStoredUsers();
    users[user.email.toLowerCase()] = user;
    localStorage.setItem(USERS_REGISTRY_KEY, JSON.stringify(users));
  } catch {
    // Ignore storage quota errors
  }
}

function getStoredSession() {
  try {
    const data = localStorage.getItem(AUTH_STORAGE_KEY);
    return data ? JSON.parse(data) : null;
  } catch {
    return null;
  }
}

function setStoredSession(user) {
  try {
    if (user) {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(user));
      saveUserToRegistry(user);
    } else {
      localStorage.removeItem(AUTH_STORAGE_KEY);
    }
  } catch {
    // Ignore storage quota errors
  }
}

export const authService = {
  /**
   * User login
   * @param {string} email 
   * @param {string} password 
   * @returns {Promise<{success: boolean, user: object, token: string}>}
   */
  async login(email, password) {
    await new Promise((res) => setTimeout(res, 500));

    if (!email || !email.trim() || !password) {
      throw new Error('Please enter both your email address and password.');
    }

    const cleanEmail = email.trim().toLowerCase();
    const existingUsers = getStoredUsers();
    let user = existingUsers[cleanEmail];

    if (!user) {
      const derivedName = cleanEmail.split('@')[0]
        ? cleanEmail.split('@')[0].charAt(0).toUpperCase() + cleanEmail.split('@')[0].slice(1)
        : 'Chef';

      user = {
        id: 'usr_' + Date.now(),
        fullName: derivedName,
        email: cleanEmail,
        avatarUrl: null, // Neutral default avatar
        status: 'Pantry Guard Active',
        temperatureUnit: 'C',
        remindersEnabled: true,
        eatFirstRoadmapEnabled: true,
        freshoBuddyEnabled: true,
      };
    }

    setStoredSession(user);

    return {
      success: true,
      token: 'mock_jwt_token_foodfresh_ai',
      user,
    };
  },

  /**
   * User registration
   * @param {object} param0 
   * @returns {Promise<{success: boolean, user: object, token: string}>}
   */
  async register({ fullName, email, password, householdType }) {
    await new Promise((res) => setTimeout(res, 600));

    if (!fullName || !fullName.trim()) {
      throw new Error('Please enter your full name or kitchen title.');
    }
    if (!email || !email.trim()) {
      throw new Error('Please enter your email address.');
    }
    if (!password) {
      throw new Error('Please create a password.');
    }

    const cleanEmail = email.trim().toLowerCase();
    const user = {
      id: 'usr_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7),
      fullName: fullName.trim(),
      email: cleanEmail,
      householdType: householdType || 'Not specified',
      avatarUrl: null, // Neutral default avatar
      status: 'Pantry Guard Active',
      temperatureUnit: 'C',
      remindersEnabled: true,
      eatFirstRoadmapEnabled: true,
      freshoBuddyEnabled: true,
    };

    setStoredSession(user);

    return {
      success: true,
      token: 'mock_jwt_token_foodfresh_ai',
      user,
    };
  },

  /**
   * Get current authenticated user
   * @returns {Promise<object|null>}
   */
  async getCurrentUser() {
    return getStoredSession();
  },

  /**
   * Update user profile & settings
   * @param {object} updates 
   * @returns {Promise<object>}
   */
  async updateProfile(updates) {
    await new Promise((res) => setTimeout(res, 300));
    const current = getStoredSession() || {
      id: 'usr_default',
      fullName: 'Kitchen Chef',
      email: '',
      avatarUrl: null,
      status: 'Pantry Guard Active',
      temperatureUnit: 'C',
      remindersEnabled: true,
      eatFirstRoadmapEnabled: true,
      freshoBuddyEnabled: true,
    };
    const updated = { ...current, ...updates };
    setStoredSession(updated);
    return updated;
  },

  /**
   * Log out current session
   * @returns {Promise<boolean>}
   */
  async logout() {
    await new Promise((res) => setTimeout(res, 200));
    setStoredSession(null);
    return true;
  },

  /**
   * Change user password placeholder
   */
  async changePassword() {
    await new Promise((res) => setTimeout(res, 400));
    return { success: true };
  },

  /**
   * Delete user account placeholder
   */
  async deleteAccount() {
    await new Promise((res) => setTimeout(res, 500));
    setStoredSession(null);
    return { success: true };
  },
};

export default authService;
