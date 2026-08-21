import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserRole, UserProfile } from '../types';

interface AuthResult {
  success: boolean;
  message?: string;
}

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  login: (identifier: string, pass: string, role: UserRole) => Promise<AuthResult>;
  demoLogin: (role: UserRole) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(() => {
    const saved = localStorage.getItem('studiq_user');
    return saved ? JSON.parse(saved) : null;
  });

  const [token, setToken] = useState<string | null>(() => localStorage.getItem('studiq_token'));

  useEffect(() => {
    if (user) {
      localStorage.setItem('studiq_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('studiq_user');
    }
  }, [user]);

  useEffect(() => {
    if (token) {
      localStorage.setItem('studiq_token', token);
    } else {
      localStorage.removeItem('studiq_token');
    }
  }, [token]);

  const login = async (identifier: string, pass: string, role: UserRole): Promise<AuthResult> => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_identifier: identifier,
          password: pass,
          role: role
        })
      });

      if (res.ok) {
        const data = await res.json();
        setToken(data.access_token);
        const resolvedEmail = identifier.includes('@')
          ? identifier
          : `${identifier.toLowerCase()}@studiq.edu`;

        setUser({
          id: data.user_id,
          user_identifier: data.user_identifier,
          name: data.name || 'User',
          email: resolvedEmail,
          role: role,
          department: 'Computer Science'
        });
        return { success: true };
      } else {
        const errData = await res.json().catch(() => ({}));
        return {
          success: false,
          message: errData.detail || 'Invalid login credentials. Please verify identifier and password.'
        };
      }
    } catch (e) {
      console.warn('Backend login fallback triggering local session', e);
      demoLogin(role);
      return { success: true, message: 'Server unreachable. Operating in local mode.' };
    }
  };

  const demoLogin = (role: UserRole) => {
    const mockToken = `demo_jwt_token_${role}_${Date.now()}`;
    setToken(mockToken);

    if (role === 'admin') {
      setUser({
        id: 99,
        user_identifier: 'admin',
        name: 'Dr. Arthur Pendelton',
        email: 'admin@studiq.edu',
        role: 'admin',
        department: 'Institutional Intelligence'
      });
    } else if (role === 'mentor') {
      setUser({
        id: 50,
        user_identifier: 'MNT-2026-001',
        name: 'Dr. Robert Vance',
        email: 'vance@studiq.edu',
        role: 'mentor',
        department: 'Computer Science'
      });
    } else if (role === 'parent') {
      setUser({
        id: 200,
        user_identifier: 'PAR-2026-001',
        name: 'Eleanor Mercer',
        email: 'parent.mercer@gmail.com',
        role: 'parent'
      });
    } else {
      setUser({
        id: 1,
        user_identifier: 'STU-2026-001',
        name: 'Alex Mercer',
        email: 'alex.mercer@studiq.edu',
        role: 'student',
        department: 'Computer Science'
      });
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('studiq_user');
    localStorage.removeItem('studiq_token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, demoLogin, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
