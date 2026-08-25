import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserRole, UserProfile } from '../types';
import { API_BASE_URL } from '../services/api';

export interface AuthResult {
  success: boolean;
  message?: string;
}

export interface ContinueResult {
  status: 'authenticated' | 'registration_required' | 'error';
  redirect?: string;
  message?: string;
  role?: UserRole;
  user_identifier?: string;
}

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  login: (identifier: string, pass: string, role: UserRole) => Promise<AuthResult>;
  continueAuth: (identifier: string, pass: string, role: UserRole) => Promise<ContinueResult>;
  setSessionTokens: (accessToken: string, userProfile: UserProfile) => void;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(() => {
    const saved = localStorage.getItem('studiq_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [token, setToken] = useState<string | null>(() => localStorage.getItem('studiq_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const setSessionTokens = (accessToken: string, userProfile: UserProfile) => {
    setToken(accessToken);
    setUser(userProfile);
    localStorage.setItem('studiq_token', accessToken);
    localStorage.setItem('studiq_user', JSON.stringify(userProfile));
  };

  // Sync token to localStorage
  useEffect(() => {
    if (token) {
      localStorage.setItem('studiq_token', token);
    } else {
      localStorage.removeItem('studiq_token');
    }
  }, [token]);

  // Sync user profile to localStorage
  useEffect(() => {
    if (user) {
      localStorage.setItem('studiq_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('studiq_user');
    }
  }, [user]);

  // Verify token and restore real user profile on mount
  useEffect(() => {
    const verifyAndRestoreUser = async () => {
      const storedToken = localStorage.getItem('studiq_token');
      if (!storedToken) {
        setUser(null);
        setIsLoading(false);
        return;
      }

      try {
        const res = await fetch(`${API_BASE_URL}/auth/me`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${storedToken}`
          }
        });

        if (res.ok) {
          const profile: UserProfile = await res.json();
          setUser(profile);
          setToken(storedToken);
        } else {
          console.warn('Session expired or invalid token on startup. Logging out.');
          logout();
        }
      } catch (err) {
        console.error('Error verifying auth session with backend:', err);
      } finally {
        setIsLoading(false);
      }
    };

    verifyAndRestoreUser();
  }, []);

  const continueAuth = async (identifier: string, pass: string, role: UserRole): Promise<ContinueResult> => {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/continue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_identifier: identifier,
          password: pass,
          role: role
        })
      });

      const data = await res.json().catch(() => ({}));

      if (res.ok) {
        if (data.status === 'authenticated' && data.access_token) {
          const userProfile: UserProfile = {
            id: data.user_id,
            user_identifier: data.user_identifier,
            name: data.name || 'User',
            email: data.email || (identifier.includes('@') ? identifier : `${identifier.toLowerCase()}@studiq.edu`),
            role: role,
            department: 'Computer Science'
          };
          setSessionTokens(data.access_token, userProfile);
          return {
            status: 'authenticated',
            redirect: data.redirect || '/student/dashboard'
          };
        } else if (data.status === 'registration_required') {
          return {
            status: 'registration_required',
            role: role,
            user_identifier: identifier,
            message: data.message || "No StudIQ account found. Let's create your account."
          };
        }
      }

      return {
        status: 'error',
        message: data.detail || 'Invalid credentials. Please check your ID/email and password.'
      };
    } catch (e: any) {
      return {
        status: 'error',
        message: 'Unable to connect to the authentication server. Please check your internet connection.'
      };
    }
  };

  const login = async (identifier: string, pass: string, role: UserRole): Promise<AuthResult> => {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_identifier: identifier,
          password: pass,
          role: role
        })
      });

      const data = await res.json().catch(() => ({}));

      if (res.ok && data.access_token) {
        const newAccessToken = data.access_token;
        setToken(newAccessToken);
        localStorage.setItem('studiq_token', newAccessToken);

        const profileRes = await fetch(`${API_BASE_URL}/auth/me`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${newAccessToken}`
          }
        });

        if (profileRes.ok) {
          const userProfile: UserProfile = await profileRes.json();
          setUser(userProfile);
          localStorage.setItem('studiq_user', JSON.stringify(userProfile));
        } else {
          const fallbackUser: UserProfile = {
            id: data.user_id,
            user_identifier: data.user_identifier,
            name: data.name || 'User',
            email: data.email || (identifier.includes('@') ? identifier : `${identifier.toLowerCase()}@studiq.edu`),
            role: role,
            department: 'Computer Science'
          };
          setUser(fallbackUser);
          localStorage.setItem('studiq_user', JSON.stringify(fallbackUser));
        }

        return { success: true };
      } else {
        return {
          success: false,
          message: data.detail || 'Invalid credentials. Please check your ID/email and password.'
        };
      }
    } catch (e: any) {
      return {
        success: false,
        message: 'Unable to connect to the authentication server. Please verify your internet connection or backend deployment.'
      };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('studiq_user');
    localStorage.removeItem('studiq_token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, continueAuth, setSessionTokens, logout, isAuthenticated: !!user, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
