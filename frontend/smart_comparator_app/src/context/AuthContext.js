import React, { createContext, useContext, useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api, setAuthToken } from '../services/api';
import { getApiErrorMessage } from '../utils/apiError';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  const loadMe = async () => {
    const { data } = await api.get('/auth/me');
    setUser(data);
  };

  useEffect(() => {
    (async () => {
      try {
        const saved = await AsyncStorage.getItem('auth_token');
        if (saved) {
          setToken(saved);
          setAuthToken(saved);
          await loadMe();
        }
      } catch {
        await AsyncStorage.removeItem('auth_token');
        setToken(null);
        setUser(null);
        setAuthToken(null);
      } finally {
        setAuthLoading(false);
      }
    })();
  }, []);

  const login = async (email, password) => {
    try {
      const { data } = await api.post('/auth/login', { email, password });
      await AsyncStorage.setItem('auth_token', data.access_token);
      setToken(data.access_token);
      setAuthToken(data.access_token);
      await loadMe();
    } catch (error) {
      throw new Error(getApiErrorMessage(error, 'Login failed'));
    }
  };

  const signup = async (name, email, password) => {
    try {
      const { data } = await api.post('/auth/signup', { name, email, password });
      await AsyncStorage.setItem('auth_token', data.access_token);
      setToken(data.access_token);
      setAuthToken(data.access_token);
      await loadMe();
    } catch (error) {
      throw new Error(getApiErrorMessage(error, 'Signup failed'));
    }
  };

  const logout = async () => {
    await AsyncStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
    setAuthToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, authLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
