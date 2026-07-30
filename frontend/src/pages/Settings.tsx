import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../api/client';
import { SkeletonText } from '../components/Skeleton';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const fetchConfig = async () => {
  const { data } = await api.get('/tenant-config/');
  return data;
};

const updateConfig = async (payload: any) => {
  const { data } = await api.patch('/tenant-config/update/', payload);
  return data;
};

const Settings: React.FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const { isRehabAdmin } = useAuth();

  const { data: config, isLoading } = useQuery({
    queryKey: ['tenant-config'],
    queryFn: fetchConfig,
    enabled: isRehabAdmin,
  });

  const [formData, setFormData] = useState({
    company_name: '',
    tagline: '',
    primary_color: '#1d5a70',
    secondary_color: '#2e9b6f',
    accent_color: '#b8892f',
    sidebar_color: '#0f2e3d',
    footer_text: '',
  });

  useEffect(() => {
    if (config) {
      setFormData({
        company_name: config.company_name || '',
        tagline: config.tagline || '',
        primary_color: config.primary_color || '#1d5a70',
        secondary_color: config.secondary_color || '#2e9b6f',
        accent_color: config.accent_color || '#b8892f',
        sidebar_color: config.sidebar_color || '#0f2e3d',
        footer_text: config.footer_text || '',
      });
    }
  }, [config]);

  const mutation = useMutation({
    mutationFn: updateConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenant-config'] });
      toast.showToast('Settings updated successfully!', 'success');
      // Update CSS variables
      const root = document.documentElement;
      root.style.setProperty('--primary-600', formData.primary_color);
      root.style.setProperty('--primary-700', formData.sidebar_color);
      root.style.setProperty('--accent', formData.secondary_color);
      root.style.setProperty('--warning', formData.accent_color);
    },
    onError: () => toast.showToast('Failed to update settings', 'error'),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  if (!isRehabAdmin) {
    return (
      <div className="flex items-center gap-2 text-sm text-secondary-500">
        <ExclamationTriangleIcon className="w-5 h-5 text-warning" />
        You don't have permission to access settings.
      </div>
    );
  }

  if (isLoading) return <div className="space-y-4"><SkeletonText width="w-3/4" /><SkeletonText width="w-1/2" /></div>;

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-secondary-800">Settings</h1>
        <p className="text-sm text-secondary-500">Customise your rehab centre's branding and appearance.</p>
      </div>

      <form onSubmit={handleSubmit} className="card p-6 space-y-4">
        <div>
          <label className="form-label">Company Name</label>
          <input type="text" className="input-field" value={formData.company_name} onChange={(e) => setFormData({ ...formData, company_name: e.target.value })} />
        </div>
        <div>
          <label className="form-label">Tagline</label>
          <input type="text" className="input-field" value={formData.tagline} onChange={(e) => setFormData({ ...formData, tagline: e.target.value })} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="form-label">Primary Color</label>
            <div className="flex items-center gap-2">
              <input type="color" className="w-10 h-10 p-0 border-0 rounded cursor-pointer" value={formData.primary_color} onChange={(e) => setFormData({ ...formData, primary_color: e.target.value })} />
              <input type="text" className="input-field flex-1" value={formData.primary_color} onChange={(e) => setFormData({ ...formData, primary_color: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="form-label">Secondary Color</label>
            <div className="flex items-center gap-2">
              <input type="color" className="w-10 h-10 p-0 border-0 rounded cursor-pointer" value={formData.secondary_color} onChange={(e) => setFormData({ ...formData, secondary_color: e.target.value })} />
              <input type="text" className="input-field flex-1" value={formData.secondary_color} onChange={(e) => setFormData({ ...formData, secondary_color: e.target.value })} />
            </div>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="form-label">Accent Color</label>
            <div className="flex items-center gap-2">
              <input type="color" className="w-10 h-10 p-0 border-0 rounded cursor-pointer" value={formData.accent_color} onChange={(e) => setFormData({ ...formData, accent_color: e.target.value })} />
              <input type="text" className="input-field flex-1" value={formData.accent_color} onChange={(e) => setFormData({ ...formData, accent_color: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="form-label">Sidebar Color</label>
            <div className="flex items-center gap-2">
              <input type="color" className="w-10 h-10 p-0 border-0 rounded cursor-pointer" value={formData.sidebar_color} onChange={(e) => setFormData({ ...formData, sidebar_color: e.target.value })} />
              <input type="text" className="input-field flex-1" value={formData.sidebar_color} onChange={(e) => setFormData({ ...formData, sidebar_color: e.target.value })} />
            </div>
          </div>
        </div>
        <div>
          <label className="form-label">Footer Text</label>
          <input type="text" className="input-field" value={formData.footer_text} onChange={(e) => setFormData({ ...formData, footer_text: e.target.value })} />
          <p className="text-xs text-secondary-500 mt-1">Appears at the bottom of every page.</p>
        </div>
        <button type="submit" disabled={mutation.isPending} className="btn-primary w-full justify-center">
          {mutation.isPending ? 'Saving...' : 'Save Settings'}
        </button>
      </form>

      <div className="card p-4">
        <h3 className="text-sm font-semibold text-secondary-700 mb-2">Preview</h3>
        <div className="p-3 rounded-lg" style={{ background: formData.primary_color, color: 'white' }}>
          <p className="text-sm font-medium">{formData.company_name || 'Your Rehab'}</p>
          <p className="text-xs opacity-80">{formData.tagline || 'Tagline'}</p>
        </div>
        <div className="mt-2 flex gap-2">
          <button className="btn-primary text-xs" style={{ background: formData.primary_color }}>Primary</button>
          <button className="btn-secondary text-xs" style={{ background: formData.secondary_color, color: 'white' }}>Secondary</button>
          <button className="btn-danger text-xs">Danger</button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
