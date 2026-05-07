import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { api } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(
    () => localStorage.getItem('sn_access_token')
  );
  const [loading, setLoading] = useState(true);

  // On mount, if we have a token, fetch the current user
  useEffect(() => {
    const token = localStorage.getItem('sn_access_token');
    if (!token) {
      setLoading(false);
      return;
    }
    api.get('/users/me')
      .then((data) => {
        if (data) setUser(data);
      })
      .catch(() => {
        // Token is invalid or expired and refresh failed — clear state
        localStorage.removeItem('sn_access_token');
        localStorage.removeItem('sn_refresh_token');
        localStorage.removeItem('sn_user_id');
        setAccessToken(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (accessTok, refreshTok) => {
    localStorage.setItem('sn_access_token', accessTok);
    localStorage.setItem('sn_refresh_token', refreshTok);
    setAccessToken(accessTok);

    // Fetch user profile immediately after login
    const userData = await api.get('/users/me');
    if (userData) {
      localStorage.setItem('sn_user_id', userData.id);
      setUser(userData);
    }
    return userData;
  }, []);

  const logout = useCallback(async () => {
    const refreshToken = localStorage.getItem('sn_refresh_token');
    try {
      await api.post('/auth/logout', { refresh_token: refreshToken });
    } catch {
      // Ignore logout errors — clear local state regardless
    }
    localStorage.removeItem('sn_access_token');
    localStorage.removeItem('sn_refresh_token');
    localStorage.removeItem('sn_user_id');
    setAccessToken(null);
    setUser(null);
  }, []);

  const updateUser = useCallback((updatedUser) => {
    setUser(updatedUser);
  }, []);

  const value = {
    user,
    accessToken,
    loading,
    login,
    logout,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
