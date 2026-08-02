import { createContext, useState, useEffect, useCallback } from 'react';
import authService from '../services/authService';

// oxlint-disable-next-line react/only-export-components
export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchCurrentUser = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const userData = await authService.me();
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCurrentUser();

    const handleLogoutEvent = () => {
      setUser(null);
    };

    window.addEventListener('auth_logout', handleLogoutEvent);
    return () => {
      window.removeEventListener('auth_logout', handleLogoutEvent);
    };
  }, [fetchCurrentUser]);

  const login = async (credentials) => {
    const data = await authService.login(credentials);
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    
    // Fetch full user object from /me or use data.user
    if (data.user) {
      setUser(data.user);
    } else {
      await fetchCurrentUser();
    }
    return data;
  };

  const register = async (userData) => {
    return authService.register(userData);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const value = {
    user,
    role: user?.role || null,
    isAuthenticated: !!user,
    loading,
    login,
    register,
    logout,
    refreshUser: fetchCurrentUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
