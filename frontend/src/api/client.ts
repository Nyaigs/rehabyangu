import axios from 'axios';

const api = axios.create({
  // Keep requests same-origin by default.  Vite proxies this path during local
  // development, so the browser never tries to reach its own `localhost:8000`
  // when the app is opened from another machine or a container.
  baseURL: import.meta.env.VITE_API_URL || '/api',
});

// The API uses the tenant slug to keep every request scoped to one facility.
// It is supplied at sign-in (or through VITE_TENANT_SLUG for a dedicated
// deployment); there must not be a guessed tenant fallback.
export const normalizeTenantSlug = (value?: string | null) => value?.trim().toLowerCase() || '';

export const getTenantSlug = () => normalizeTenantSlug(
  localStorage.getItem('tenant_slug') || import.meta.env.VITE_TENANT_SLUG,
);

/** Resolve Django FileField values for both Vite proxy and deployed API URLs. */
export const resolveMediaUrl = (value?: string | null): string | undefined => {
  if (!value) return undefined;
  if (/^https?:\/\//i.test(value) || value.startsWith('data:') || value.startsWith('blob:')) return value;
  const apiBase = import.meta.env.VITE_API_URL || '/api';
  if (apiBase.startsWith('http')) return new URL(value, apiBase).toString();
  return value.startsWith('/') ? value : `/${value}`;
};

api.interceptors.request.use(
  (config) => {
    const tenantSlug = getTenantSlug();
    if (tenantSlug) {
      config.headers['X-Tenant'] = tenantSlug;
    }
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const { data } = await api.post('/token/refresh/', { refresh });
          localStorage.setItem('access_token', data.access);
          originalRequest.headers.Authorization = `Bearer ${data.access}`;
          return api(originalRequest);
        } catch (e) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
