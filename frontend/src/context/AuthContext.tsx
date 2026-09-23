import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import api, { normalizeTenantSlug, resolveMediaUrl } from '../api/client';
import { displayRole as toDisplayRole } from '../utils/roles';

export interface TenantBranding {
  primary_color?: string;
  secondary_color?: string;
  accent_color?: string;
  sidebar_color?: string;
  font_family?: string;
  company_name?: string;
  tagline?: string | null;
  footer_text?: string;
  logo_url?: string | null;
  letterhead_url?: string | null;
  favicon_url?: string | null;
  onboarding_completed_at?: string | null;
  mpesa_shortcode?: string;
  mpesa_shortcode_type?: 'paybill' | 'till';
  mpesa_credentials_configured?: boolean;
  kra_pin?: string;
  bank_name?: string;
  bank_account_name?: string;
  bank_account_number?: string;
  bank_branch?: string;
  invoice_terms?: string;
  invoice_footer_text?: string;
}

interface AuthContextType {
  user: any | null;
  isSuperAdmin: boolean;
  isPlatformAdmin: boolean;
  isRehabAdmin: boolean;
  tenantName: string | null;
  displayRole: string;
  permissions: string[];
  tenantBranding: TenantBranding | null;
  login: (username: string, password: string, tenantSlug: string) => Promise<boolean>;
  logout: () => Promise<void>;
  isLoading: boolean;
  refreshAuth: () => Promise<void>;
  setTenantBranding: (branding: TenantBranding) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<any | null>(null);
  const [permissions, setPermissions] = useState<string[]>([]);
  const [tenantBranding, setTenantBranding] = useState<TenantBranding | null>(null);
  const [isPlatformAdmin, setIsPlatformAdmin] = useState(
    () => localStorage.getItem('is_platform_admin') === 'true'
  );
  const [isLoading, setIsLoading] = useState(true);

  const reset = () => {
    setUser(null);
    setPermissions([]);
    setTenantBranding(null);
    setIsPlatformAdmin(false);
  };

  useEffect(() => {
    const root = document.documentElement;
    const branding = tenantBranding;
    root.style.setProperty('--tenant-primary', branding?.primary_color || '#1D5A70');
    root.style.setProperty('--tenant-secondary', branding?.secondary_color || '#5B6B76');
    root.style.setProperty('--tenant-accent', branding?.accent_color || '#237A57');
    root.style.setProperty('--tenant-sidebar', branding?.sidebar_color || '#0F2E3D');
    root.style.setProperty('--tenant-font', branding?.font_family || 'Inter, sans-serif');

    if (branding?.favicon_url) {
      let icon = document.querySelector<HTMLLinkElement>('link[rel="icon"]');
      if (!icon) {
        icon = document.createElement('link');
        icon.rel = 'icon';
        document.head.appendChild(icon);
      }
      icon.href = resolveMediaUrl(branding.favicon_url) || '/favicon.svg';
    }
  }, [tenantBranding]);

  const refreshAuth = async () => {
    // The identity request is essential. Permissions and branding enrich the
    // workspace but must not turn a successful token login into a false login
    // failure if an optional configuration record is missing or unavailable.
    const userRes = await api.get('/users/me/');
    setUser(userRes.data);

    const platform =
      localStorage.getItem('is_platform_admin') === 'true' &&
      Boolean(userRes.data?.is_superuser);
    setIsPlatformAdmin(platform);

    if (platform) {
      setPermissions([]);
      setTenantBranding(null);
      return;
    }

    const [permissionsResult, brandingResult] = await Promise.allSettled([
      api.get('/user/permissions/'),
      api.get('/tenant-config/'),
    ]);

    setPermissions(
      permissionsResult.status === 'fulfilled'
        ? permissionsResult.value.data.permissions ?? permissionsResult.value.data ?? []
        : []
    );
    setTenantBranding(
      brandingResult.status === 'fulfilled' ? brandingResult.value.data : null
    );
  };

  useEffect(() => {
    if (!localStorage.getItem('access_token')) {
      setIsLoading(false);
      return;
    }
    refreshAuth()
      .catch(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        reset();
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = async (username: string, password: string, tenantSlug: string) => {
    const normalizedTenantSlug = normalizeTenantSlug(tenantSlug);
    if (!normalizedTenantSlug) {
      throw new Error('Enter your facility workspace to sign in.');
    }

    // Save the same normalized slug that is sent in the request. This keeps
    // the token request and every subsequent authenticated request in sync.
    localStorage.setItem('tenant_slug', normalizedTenantSlug);

    const { data } = await api.post(
      '/token/',
      { username, password },
      { headers: { 'X-Tenant': normalizedTenantSlug } }
    );

    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    localStorage.setItem('is_platform_admin', data.is_platform_admin ? 'true' : 'false');

    await refreshAuth();
    return Boolean(data.is_platform_admin);
  };

  const logout = async () => {
    const refresh = localStorage.getItem('refresh_token');
    try {
      await api.post('/auth/logout/', refresh ? { refresh } : {});
    } catch {
      /* Clear the local session even if the network is already unavailable. */
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('tenant_slug');
      localStorage.removeItem('is_platform_admin');
      reset();
    }
  };

  const isSuperAdmin = Boolean(user?.is_superuser);
  const isRehabAdmin = Boolean(user?.is_rehab_admin || isSuperAdmin);

  const value: AuthContextType = {
    user,
    isSuperAdmin,
    isPlatformAdmin,
    isRehabAdmin,
    displayRole: toDisplayRole(user),
    tenantName: isPlatformAdmin
      ? 'RehabYangu Platform Administration'
      : tenantBranding?.company_name || user?.tenant_name || null,
    permissions,
    tenantBranding,
    setTenantBranding,
    login,
    logout,
    isLoading,
    refreshAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
