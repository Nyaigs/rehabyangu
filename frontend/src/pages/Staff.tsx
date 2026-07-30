import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PlusIcon, UserIcon, XMarkIcon, UserPlusIcon } from '@heroicons/react/24/outline';
import api from '../api/client';
import { SkeletonTable, SkeletonText } from '../components/Skeleton';
import { EmptyState } from '../components/EmptyState';
import { useToast } from '../context/ToastContext';

const fetchStaff = async () => {
  const { data } = await api.get('/staff/');
  return data;
};

const createStaff = async (payload: any) => {
  const { data } = await api.post('/staff/create/', payload);
  return data;
};

const Staff: React.FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    role: 'other',
    first_name: '',
    last_name: '',
  });
  const [error, setError] = useState('');

  const { data: staff, isLoading } = useQuery({
    queryKey: ['staff'],
    queryFn: fetchStaff,
  });

  const mutation = useMutation({
    mutationFn: createStaff,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['staff'] });
      setShowForm(false);
      setFormData({ username: '', email: '', password: '', role: 'other', first_name: '', last_name: '' });
      toast.showToast('Staff created successfully', 'success');
    },
    onError: (error: any) => {
      setError(error.response?.data?.error || 'Failed to create staff');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    mutation.mutate(formData);
  };

  const roles = [
    { value: 'psychiatrist', label: 'Psychiatrist' },
    { value: 'clinical_officer', label: 'Clinical Officer' },
    { value: 'nurse', label: 'Nurse' },
    { value: 'counselor', label: 'Counselor' },
    { value: 'pharmacist', label: 'Pharmacist' },
    { value: 'receptionist', label: 'Receptionist' },
    { value: 'accountant', label: 'Accountant' },
    { value: 'store_manager', label: 'Store Manager' },
    { value: 'hr_manager', label: 'HR Manager' },
    { value: 'cook', label: 'Cook' },
    { value: 'other', label: 'Other' },
  ];

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div>
          <SkeletonText width="w-32" className="mb-1" />
          <SkeletonText width="w-48" />
        </div>
        <SkeletonTable rows={5} cols={4} />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <h1 className="text-2xl font-bold text-secondary-800">Staff Management</h1>
          <p className="text-sm text-secondary-500">Manage your team members and their roles.</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary">
          <PlusIcon className="w-4 h-4" />
          Add Staff
        </button>
      </div>

      {staff?.length === 0 ? (
        <EmptyState
          title="No staff members"
          description="Add your first staff member to start building your team."
          actionLabel="Add Staff"
          onAction={() => setShowForm(true)}
          iconType="users"
        />
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {staff?.map((s: any) => (
                <tr key={s.id}>
                  <td className="font-medium text-secondary-800 flex items-center gap-2">
                    <UserIcon className="w-4 h-4 text-secondary-400" />
                    {s.full_name || s.username}
                  </td>
                  <td>{s.username}</td>
                  <td>{s.email}</td>
                  <td><span className="badge badge-draft capitalize">{s.role.replace('_', ' ')}</span></td>
                  <td>
                    {s.is_rehab_admin ? (
                      <span className="badge badge-active">Admin</span>
                    ) : (
                      <span className="badge badge-draft">Staff</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-content animate-scaleIn" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-secondary-800">Add Staff Member</h2>
              <button onClick={() => setShowForm(false)} className="text-secondary-400 hover:text-secondary-600">
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="space-y-3">
                <div>
                  <label className="form-label">First Name</label>
                  <input type="text" className="input-field" value={formData.first_name} onChange={(e) => setFormData({ ...formData, first_name: e.target.value })} />
                </div>
                <div>
                  <label className="form-label">Last Name</label>
                  <input type="text" className="input-field" value={formData.last_name} onChange={(e) => setFormData({ ...formData, last_name: e.target.value })} />
                </div>
                <div>
                  <label className="form-label">Username *</label>
                  <input type="text" className="input-field" value={formData.username} onChange={(e) => setFormData({ ...formData, username: e.target.value })} required />
                </div>
                <div>
                  <label className="form-label">Email *</label>
                  <input type="email" className="input-field" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} required />
                </div>
                <div>
                  <label className="form-label">Password *</label>
                  <input type="password" className="input-field" value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} required minLength={6} />
                </div>
                <div>
                  <label className="form-label">Role *</label>
                  <select className="input-field" value={formData.role} onChange={(e) => setFormData({ ...formData, role: e.target.value })} required>
                    {roles.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
                  </select>
                </div>
                {error && <p className="text-danger text-sm">{error}</p>}
                <div className="flex gap-2">
                  <button type="submit" disabled={mutation.isPending} className="btn-primary flex-1 justify-center">
                    {mutation.isPending ? 'Creating...' : 'Create Staff'}
                  </button>
                  <button type="button" onClick={() => setShowForm(false)} className="btn-secondary flex-1 justify-center">Cancel</button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Staff;
