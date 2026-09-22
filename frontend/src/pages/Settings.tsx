import React, { useEffect, useState } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { ErrorBanner } from '../components/ErrorBanner';
import { resolveMediaUrl } from '../api/client';

const schema = z.object({ company_name: z.string().min(1, 'Facility name is required'), tagline: z.string(), logo: z.any().optional(), letterhead: z.any().optional() });
type FormValues = z.infer<typeof schema>;

const Settings: React.FC = () => {
  const { isRehabAdmin, tenantBranding, setTenantBranding } = useAuth();
  const toast = useToast();
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [letterheadPreview, setLetterheadPreview] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState('');
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { company_name: '', tagline: '' } });
  useEffect(() => { if (tenantBranding) reset({ company_name: tenantBranding.company_name || '', tagline: '' }); }, [tenantBranding, reset]);
  const preview = (file: File | undefined, setter: (value: string | null) => void) => { if (file) setter(URL.createObjectURL(file)); };
  const submit = async (values: FormValues) => {
    setSubmitError('');
    const body = new FormData();
    body.append('company_name', values.company_name); body.append('tagline', values.tagline || '');
    const logo = values.logo?.[0] as File | undefined; const letterhead = values.letterhead?.[0] as File | undefined;
    if (logo) body.append('logo', logo); if (letterhead) body.append('letterhead', letterhead);
    try { const { data } = await api.put('/tenant-config/', body); setTenantBranding(data); toast.showToast('Branding updated successfully', 'success'); }
    catch (error: any) { const message = getApiError(error.response?.data) || 'Unable to update branding'; setSubmitError(message); toast.showToast(message, 'error'); }
  };
  if (!isRehabAdmin) return <div className="card p-6 text-sm text-secondary-500">Only your rehab administrator can update facility branding.</div>;
  return <div className="max-w-3xl space-y-6"><div><h1 className="text-2xl font-bold text-secondary-800">Facility settings</h1><p className="text-sm text-secondary-500">Keep your team workspace and future documents on brand.</p></div><form onSubmit={handleSubmit(submit)} className="card space-y-6 p-6">{submitError && <ErrorBanner>{submitError}</ErrorBanner>}
    <div className="grid gap-4 sm:grid-cols-2"><label><span className="form-label">Facility name</span><input className="input-field" {...register('company_name')} />{errors.company_name && <span className="text-xs text-danger">{errors.company_name.message}</span>}</label><label><span className="form-label">Tagline</span><input className="input-field" {...register('tagline')} placeholder="Exceptional care, connected" /></label></div>
    <div className="grid gap-6 md:grid-cols-2"><Upload label="Header logo" hint="PNG, JPEG, WebP, SVG, or ICO; up to 2 MiB." current={logoPreview || resolveMediaUrl(tenantBranding?.logo_url)} accept="image/png,image/jpeg,image/webp,image/svg+xml,image/x-icon,image/vnd.microsoft.icon" input={register('logo', { onChange: (event) => preview(event.target.files?.[0], setLogoPreview) })} /><Upload label="Letterhead" hint="PNG, JPEG, WebP, SVG, or ICO; up to 2 MiB." current={letterheadPreview || resolveMediaUrl(tenantBranding?.letterhead_url)} accept="image/png,image/jpeg,image/webp,image/svg+xml,image/x-icon,image/vnd.microsoft.icon" input={register('letterhead', { onChange: (event) => preview(event.target.files?.[0], setLetterheadPreview) })} /></div>
    <button disabled={isSubmitting} className="btn-primary">{isSubmitting ? 'Saving…' : 'Save branding'}</button>
  </form></div>;
};
function Upload({ label, hint, current, accept, input }: { label: string; hint: string; current?: string | null; accept: string; input: any }) { return <label className="block"><span className="form-label">{label}</span><div className="mt-1 flex min-h-32 items-center justify-center overflow-hidden rounded-xl border border-dashed border-slate-300 bg-slate-50 p-3">{current ? <img src={current} alt={`${label} preview`} className="max-h-28 max-w-full object-contain" /> : <span className="text-xs text-slate-400">No image selected</span>}</div><input type="file" accept={accept} className="mt-3 block w-full text-sm text-secondary-600" {...input} /><p className="mt-1 text-xs text-secondary-500">{hint}</p></label>; }
function getApiError(data: unknown): string | null { if (!data || typeof data !== 'object') return null; const value = Object.values(data as Record<string, unknown>)[0]; return typeof value === 'string' ? value : Array.isArray(value) && typeof value[0] === 'string' ? value[0] : null; }
export default Settings;
