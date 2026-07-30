import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  PlusIcon,
  EyeIcon,
  UserGroupIcon,
  CreditCardIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import api from '../../api/client';

// --- API helpers ---
const fetchTenants = async () => {
  const { data } = await api.get('/tenants/');
  return data;
};

const fetchStats = async () => {
  const { data } = await api.get('/tenants/stats/');
  return data;
};

const toggleTenantStatus = async ({ id, status }: { id: number; status: string }) => {
  const { data } = await api.patch(`/tenants/${id}/toggle-status/`, { status });
  return data;
};

const extendTrial = async ({ id, days }: { id: number; days: number }) => {
  const { data } = await api.post(`/tenants/${id}/extend-trial/`, { days });
  return data;
};

const fetchTenantStaff = async (id: number) => {
  const { data } = await api.get(`/tenants/${id}/staff/`);
  return data;
};

const recordPayment = async (payload: any) => {
  const { data } = await api.post('/record-payment/', payload);
  return data;
};

// --- Status Badge ---
const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const config = {
    active: { color: 'badge-active', icon: CheckCircleIcon, label: 'Active' },
    trial: { color: 'badge-trial', icon: ClockIcon, label: 'Trial' },
    overdue: { color: 'badge-overdue', icon: ExclamationTriangleIcon, label: 'Overdue' },
    suspended: { color: 'badge-suspended', icon: XCircleIcon, label: 'Suspended' },
  };
  const { color, icon: Icon, label } = config[status as keyof typeof config] || config.trial;
  return (
    <span className={`badge ${color}`}>
      <Icon className="w-3 h-3" />
      {label}
    </span>
  );
};

// --- KPI Card ---
const KPICard: React.FC<{ title: string; value: number; icon: React.ElementType; color: string }> = ({
  title, value, icon: Icon, color,
}) => (
  <div className="kpi-card">
    <div>
      <div className="kpi-label">{title}</div>
      <div className="kpi-value">{value}</div>
    </div>
    <Icon className="kpi-icon" style={{ color }} />
  </div>
);

// --- Staff Modal ---
const StaffModal: React.FC<{ tenantId: number; tenantName: string; onClose: () => void }> = ({
  tenantId, tenantName, onClose,
}) => {
  const { data: staff, isLoading } = useQuery({
    queryKey: ['tenant-staff', tenantId],
    queryFn: () => fetchTenantStaff(tenantId),
  });

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content animate-scaleIn" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-lg font-semibold text-secondary-800 mb-2">Staff – {tenantName}</h2>
        {isLoading ? (
          <p>Loading...</p>
        ) : staff && staff.length > 0 ? (
          <ul className="divide-y divide-secondary-100">
            {staff.map((s: any) => (
              <li key={s.id} className="py-2">
                <p className="font-medium">{s.full_name || s.username}</p>
                <p className="text-sm text-secondary-500">{s.email}</p>
                <p className="text-xs text-secondary-400">Role: {s.role}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-secondary-500">No staff found.</p>
        )}
        <button onClick={onClose} className="btn-secondary w-full justify-center mt-4">Close</button>
      </div>
    </div>
  );
};

// --- Record Payment Modal ---
const RecordPaymentModal: React.FC<{
  tenantId: number;
  tenantName: string;
  onClose: () => void;
  onSuccess: () => void;
}> = ({ tenantId, tenantName, onClose, onSuccess }) => {
  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState('mpesa');
  const [reference, setReference] = useState('');
  const [paidThroughDate, setPaidThroughDate] = useState('');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState('');

  const mutation = useMutation({
    mutationFn: recordPayment,
    onSuccess: () => { onSuccess(); onClose(); },
    onError: (error: any) => setError(error.response?.data?.error || 'Failed to record payment'),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!amount || parseFloat(amount) <= 0) return setError('Please enter a valid amount');
    if (!paidThroughDate) return setError('Please select the paid-through date');
    mutation.mutate({
      tenant_id: tenantId,
      amount: parseFloat(amount),
      method,
      reference,
      notes,
      paid_through_date: paidThroughDate,
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content animate-scaleIn" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-lg font-semibold text-secondary-800 mb-2">Record Payment – {tenantName}</h2>
        <form onSubmit={handleSubmit}>
          <div className="space-y-3">
            <div>
              <label className="form-label">Amount (KES) *</label>
              <input type="number" step="0.01" className="input-field" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="e.g. 25000" required />
            </div>
            <div>
              <label className="form-label">Payment Method *</label>
              <select className="input-field" value={method} onChange={(e) => setMethod(e.target.value)} required>
                <option value="mpesa">M-Pesa</option>
                <option value="bank">Bank Transfer</option>
                <option value="cash">Cash</option>
              </select>
            </div>
            <div>
              <label className="form-label">Reference</label>
              <input type="text" className="input-field" value={reference} onChange={(e) => setReference(e.target.value)} placeholder="M-Pesa code or cheque number" />
            </div>
            <div>
              <label className="form-label">Paid Through Date *</label>
              <input type="date" className="input-field" value={paidThroughDate} onChange={(e) => setPaidThroughDate(e.target.value)} required />
              <p className="text-xs text-secondary-500 mt-1">Subscription active until this date.</p>
            </div>
            <div>
              <label className="form-label">Notes</label>
              <textarea className="input-field" value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} placeholder="Additional notes..." />
            </div>
            {error && <p className="text-danger text-sm">{error}</p>}
            <div className="flex gap-2">
              <button type="submit" disabled={mutation.isPending} className="btn-primary flex-1 justify-center">
                {mutation.isPending ? 'Processing...' : 'Record Payment'}
              </button>
              <button type="button" onClick={onClose} className="btn-secondary flex-1 justify-center">Cancel</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

// --- Tenant Form ---
const TenantForm: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    tenant_name: '',
    subdomain: '',
    admin_name: '',
    admin_email: '',
    admin_password: '',
  });
  const [error, setError] = useState('');

  const mutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/tenants/create/', formData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenants'] });
      queryClient.invalidateQueries({ queryKey: ['tenant-stats'] });
      onClose();
    },
    onError: (error: any) => setError(error.response?.data?.error || 'Failed to create tenant'),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    mutation.mutate();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content animate-scaleIn" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-lg font-semibold text-secondary-800 mb-4">Add New Rehab Centre</h2>
        <form onSubmit={handleSubmit}>
          <div className="space-y-3">
            <div>
              <label className="form-label">Rehab Name *</label>
              <input type="text" className="input-field" value={formData.tenant_name} onChange={(e) => setFormData({ ...formData, tenant_name: e.target.value })} required />
            </div>
            <div>
              <label className="form-label">Subdomain *</label>
              <input type="text" className="input-field" placeholder="e.g. serenity" value={formData.subdomain} onChange={(e) => setFormData({ ...formData, subdomain: e.target.value.toLowerCase() })} required />
              <p className="text-xs text-secondary-500 mt-1">Will be used for login URL: {formData.subdomain}.rehabyangu.com</p>
            </div>
            <div>
              <label className="form-label">Admin Name *</label>
              <input type="text" className="input-field" value={formData.admin_name} onChange={(e) => setFormData({ ...formData, admin_name: e.target.value })} required />
            </div>
            <div>
              <label className="form-label">Admin Email *</label>
              <input type="email" className="input-field" value={formData.admin_email} onChange={(e) => setFormData({ ...formData, admin_email: e.target.value })} required />
            </div>
            <div>
              <label className="form-label">Admin Password *</label>
              <input type="password" className="input-field" value={formData.admin_password} onChange={(e) => setFormData({ ...formData, admin_password: e.target.value })} required minLength={6} />
            </div>
            {error && <p className="text-danger text-sm">{error}</p>}
            <div className="flex gap-2">
              <button type="submit" disabled={mutation.isPending} className="btn-primary flex-1 justify-center">
                {mutation.isPending ? 'Creating...' : 'Create Rehab'}
              </button>
              <button type="button" onClick={onClose} className="btn-secondary flex-1 justify-center">Cancel</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

// --- Main Page ---
const Tenants: React.FC = () => {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [showStaffModal, setShowStaffModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedTenant, setSelectedTenant] = useState<{ id: number; name: string } | null>(null);

  const { data: tenants, isLoading: tenantsLoading } = useQuery({ queryKey: ['tenants'], queryFn: fetchTenants });
  const { data: stats, isLoading: statsLoading } = useQuery({ queryKey: ['tenant-stats'], queryFn: fetchStats });

  const toggleMutation = useMutation({
    mutationFn: toggleTenantStatus,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenants'] });
      queryClient.invalidateQueries({ queryKey: ['tenant-stats'] });
    },
  });

  const extendMutation = useMutation({
    mutationFn: extendTrial,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenants'] });
      queryClient.invalidateQueries({ queryKey: ['tenant-stats'] });
    },
  });

  const handleToggle = (id: number, currentStatus: string) => {
    const newStatus = currentStatus === 'suspended' ? 'active' : 'suspended';
    if (window.confirm(`Are you sure you want to ${newStatus === 'suspended' ? 'suspend' : 'activate'} this tenant?`)) {
      toggleMutation.mutate({ id, status: newStatus });
    }
  };

  const handleExtendTrial = (id: number) => {
    const days = prompt('Enter number of days to extend trial:', '7');
    if (days && !isNaN(Number(days))) {
      extendMutation.mutate({ id, days: parseInt(days) });
    }
  };

  const handlePaymentSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['tenants'] });
    queryClient.invalidateQueries({ queryKey: ['tenant-stats'] });
  };

  if (tenantsLoading || statsLoading) return <div className="p-4 text-sm">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <h1 className="text-2xl font-bold text-secondary-800">Rehab Centres</h1>
          <p className="text-sm text-secondary-500">Manage all rehabs using the platform</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary">
          <PlusIcon className="w-4 h-4" />
          Add Rehab Centre
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <KPICard title="Total Rehabs" value={stats?.total_tenants || 0} icon={UserGroupIcon} color="#1d5a70" />
        <KPICard title="Active" value={stats?.active_tenants || 0} icon={CheckCircleIcon} color="#2e9b6f" />
        <KPICard title="Overdue" value={stats?.overdue_tenants || 0} icon={ExclamationTriangleIcon} color="#b8892f" />
        <KPICard title="Suspended" value={stats?.suspended_tenants || 0} icon={XCircleIcon} color="#b24b3e" />
      </div>

      {/* Tenant Table */}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Rehab</th>
              <th>Plan</th>
              <th>Status</th>
              <th>Staff</th>
              <th>Patients</th>
              <th className="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {tenants?.map((tenant: any) => (
              <tr key={tenant.id}>
                <td>
                  <div className="font-medium text-secondary-800">{tenant.name}</div>
                  <div className="text-xs text-secondary-500">{tenant.subdomain}.rehabyangu.com</div>
                </td>
                <td className="capitalize">{tenant.plan}</td>
                <td><StatusBadge status={tenant.status} /></td>
                <td>{tenant.user_count}</td>
                <td>{tenant.patient_count}</td>
                <td className="text-right">
                  <div className="flex flex-wrap justify-end gap-1">
                    <button
                      onClick={() => { setSelectedTenant({ id: tenant.id, name: tenant.name }); setShowStaffModal(true); }}
                      className="text-secondary-500 hover:text-primary-600 text-xs flex items-center gap-1"
                    >
                      <EyeIcon className="w-4 h-4" />
                      <span className="hidden sm:inline">Staff</span>
                    </button>
                    <button
                      onClick={() => { setSelectedTenant({ id: tenant.id, name: tenant.name }); setShowPaymentModal(true); }}
                      className="text-secondary-500 hover:text-accent text-xs flex items-center gap-1"
                    >
                      <CreditCardIcon className="w-4 h-4" />
                      <span className="hidden sm:inline">Pay</span>
                    </button>
                    <button
                      onClick={() => handleToggle(tenant.id, tenant.status)}
                      className={`text-xs ${tenant.status === 'suspended' ? 'text-accent hover:text-accent-dark' : 'text-danger hover:text-danger-dark'}`}
                    >
                      {tenant.status === 'suspended' ? 'Activate' : 'Suspend'}
                    </button>
                    {tenant.status === 'trial' && (
                      <button onClick={() => handleExtendTrial(tenant.id)} className="text-xs text-warning hover:text-warning-dark">
                        Extend
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showForm && <TenantForm onClose={() => setShowForm(false)} />}
      {showStaffModal && selectedTenant && (
        <StaffModal
          tenantId={selectedTenant.id}
          tenantName={selectedTenant.name}
          onClose={() => { setShowStaffModal(false); setSelectedTenant(null); }}
        />
      )}
      {showPaymentModal && selectedTenant && (
        <RecordPaymentModal
          tenantId={selectedTenant.id}
          tenantName={selectedTenant.name}
          onClose={() => { setShowPaymentModal(false); setSelectedTenant(null); }}
          onSuccess={handlePaymentSuccess}
        />
      )}
    </div>
  );
};

export default Tenants;
