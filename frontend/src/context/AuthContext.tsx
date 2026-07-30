import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import api from '../api/client';

interface AuthContextType {
  user: any | null;
  isSuperAdmin: boolean;
  isRehabAdmin: boolean;
  tenantName: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<any | null>(null);
  const [isSuperAdmin, setIsSuperAdmin] = useState<boolean>(false);
  const [isRehabAdmin, setIsRehabAdmin] = useState<boolean>(false);
  const [tenantName, setTenantName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      api.get('/users/me/')
        .then((res) => {
          const data = res.data;
          setUser(data);
          setIsSuperAdmin(data.is_superuser || false);
          setIsRehabAdmin(data.is_rehab_admin || false);
          setTenantName(data.tenant_name || null);
        })
        .catch(() => {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          setUser(null);
          setIsSuperAdmin(false);
          setIsRehabAdmin(false);
          setTenantName(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (username: string, password: string) => {
    const { data } = await api.post('/token/', { username, password });
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    const userRes = await api.get('/users/me/');
    setUser(userRes.data);
    setIsSuperAdmin(userRes.data.is_superuser || false);
    setIsRehabAdmin(userRes.data.is_rehab_admin || false);
    setTenantName(userRes.data.tenant_name || null);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setIsSuperAdmin(false);
    setIsRehabAdmin(false);
    setTenantName(null);
  };

  return (
    <AuthContext.Provider value={{ user, isSuperAdmin, isRehabAdmin, tenantName, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
