/**
 * User storage utility to ensure complete data isolation between user accounts.
 */

const AUTH_STORAGE_KEY = 'foodfresh_ai_session';

export function getCurrentUserId() {
  try {
    const data = localStorage.getItem(AUTH_STORAGE_KEY);
    if (data) {
      const user = JSON.parse(data);
      if (user && user.id) return user.id;
      if (user && user.email) return 'usr_' + user.email.toLowerCase().replace(/[^a-z0-9]/g, '_');
    }
  } catch {
    // ignore
  }
  return 'default_guest';
}
