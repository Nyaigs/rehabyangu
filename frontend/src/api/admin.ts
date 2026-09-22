import api from './client';

export type Plan = { id: number; name: string; code: string; description: string; price_monthly: string; max_users: number | null; feature_flags: Record<string, boolean>; is_active: boolean };
export type TenantMember = { name: string; email: string; role: string; is_rehab_admin: boolean; tenant_user_id: string | null; is_active: boolean; last_login: string | null };
export type Tenant = { id: number; name: string; subdomain: string; logo_url?: string | null; status: 'active' | 'trial' | 'overdue' | 'suspended'; is_active: boolean; archived_at?: string | null; plan: Plan | null; monthly_fee?: string; user_count: number; active_user_count?: number; active_member_count?: number; max_users: number | null; remaining_users: number | null; trial_ends_at: string | null; next_billing_date: string | null; grace_period_end: string | null; days_remaining?: number | null; billing_cycle: string };
export type PlatformStats = { total_tenants: number; active_tenants: number; trial_tenants: number; overdue_tenants: number; suspended_tenants: number; new_tenants_this_month: number; total_users: number; mrr: string };

export const adminApi = {
  stats: async () => (await api.get<PlatformStats>('/admin/stats/')).data,
  tenants: async (params: Record<string, string | number | undefined> = {}) => (await api.get<{ results: Tenant[] }>('/admin/tenants/', { params })).data,
  tenant: async (id: string) => (await api.get<Tenant & { administrator?: { name: string; email: string }; members?: TenantMember[]; recent_audit_events?: { actor: string; action: string; description: string; timestamp: string }[] }>(`/admin/tenants/${id}/`)).data,
  createTenant: async (body: Record<string, unknown>) => (await api.post('/admin/tenants/', body)).data,
  updateTenant: async (id: number, body: Record<string, unknown>) => (await api.patch<Tenant>(`/admin/tenants/${id}/`, body)).data,
  sendPaymentReminder: async (id: number) => (await api.post<{ message: string; sent: boolean }>(`/admin/tenants/${id}/payment-reminder/`)).data,
  plans: async () => (await api.get<Plan[]>('/admin/plans/')).data,
  createPlan: async (body: Partial<Plan>) => (await api.post<Plan>('/admin/plans/', body)).data,
  updatePlan: async (id: number, body: Partial<Plan>) => (await api.patch<Plan>(`/admin/plans/${id}/`, body)).data,
};
