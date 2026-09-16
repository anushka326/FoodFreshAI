import { useState, useEffect } from 'react';
import { authService } from '../services/authService.js';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authService.getCurrentUser().then((userData) => {
      setUser(userData);
      setLoading(false);
    });
  }, []);

  const login = async (email, password) => {
    const res = await authService.login(email, password);
    setUser(res.user);
    return res;
  };

  const register = async (formData) => {
    const res = await authService.register(formData);
    setUser(res.user);
    return res;
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const updateProfile = async (updates) => {
    const updated = await authService.updateProfile(updates);
    setUser(updated);
    return updated;
  };

  return {
    user,
    loading,
    updateProfile,
    login,
    register,
    logout,
  };
}

export default useAuth;
