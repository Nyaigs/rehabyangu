import { useMemo, useState, type ReactNode } from 'react';
import { useNavigate } from '@tanstack/react-router';
import api, { resolveMediaUrl } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { ErrorBanner } from '../components/ErrorBanner';

type FormState = { company_name: string; tagline: string; primary_color: string; logo: File | null; invite_email: string; invite_role: string };

export default function Onboarding() {
  const navigate = useNavigate();
  const { tenantBranding, setTenantBranding } = useAuth();
  const [step, setStep] = useState(1);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState<FormState>({
    company_name: tenantBranding?.company_name || '', tagline: tenantBranding?.tagline || '',
    primary_color: tenantBranding?.primary_color || '#17614F', logo: null, invite_email: '', invite_role: 'Clinician',
  });
  const preview = useMemo(() => form.logo ? URL.createObjectURL(form.logo) : resolveMediaUrl(tenantBranding?.logo_url) || null, [form.logo, tenantBranding?.logo_url]);
  const set = <K extends keyof FormState>(key: K, value: FormState[K]) => setForm((current) => ({ ...current, [key]: value }));

  const next = () => {
    if (step === 1 && !form.company_name.trim()) return setError('Enter your facility name to continue.');
    if (step === 3 && form.invite_email && !/^\S+@\S+\.\S+$/.test(form.invite_email)) return setError('Enter a valid staff email address, or leave it blank to skip this step.');
    setError(''); setStep((current) => Math.min(4, current + 1));
  };
  const submit = async () => {
    setError(''); setSubmitting(true);
    try {
      const payload = new FormData();
      payload.set('company_name', form.company_name.trim()); payload.set('tagline', form.tagline.trim());
      payload.set('primary_color', form.primary_color);
      if (form.logo) payload.set('logo', form.logo);
      await api.put('/tenant-config/', payload);
      if (form.invite_email) await api.post('/staff/create/', { email: form.invite_email, first_name: '', last_name: '', role: form.invite_role, extra_permissions: [] });
      const { data } = await api.put('/tenant-config/', { complete_onboarding: true });
      setTenantBranding(data);
      navigate({ to: '/' });
    } catch (requestError: any) { setError(getApiError(requestError.response?.data) || 'We could not save your facility setup. Please try again.'); }
    finally { setSubmitting(false); }
  };

  return <main className="min-h-screen bg-slate-50 p-5 sm:p-10"><section className="mx-auto max-w-2xl rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 sm:p-9"><p className="text-sm font-semibold" style={{ color: 'var(--tenant-primary)' }}>Facility setup</p><h1 className="mt-1 text-3xl font-bold text-slate-900">Welcome to RehabYangu</h1><p className="mt-2 text-sm text-slate-600">Set up your workspace in a few quick steps.</p><ol className="mt-7 grid grid-cols-4 gap-2">{['Facility', 'Brand', 'Team', 'Review'].map((label, index) => <li key={label} className="text-center text-xs font-medium"><span style={index + 1 <= step ? { backgroundColor: 'var(--tenant-primary)' } : undefined} className={`mx-auto mb-2 grid h-7 w-7 place-items-center rounded-full ${index + 1 <= step ? 'text-white' : 'bg-slate-100 text-slate-500'}`}>{index + 1}</span>{label}</li>)}</ol>{error && <div className="mt-6"><ErrorBanner>{error}</ErrorBanner></div>}<div className="mt-8">{step === 1 && <div className="space-y-4"><Field label="Facility name"><input autoFocus className="input-field" value={form.company_name} onChange={(event) => set('company_name', event.target.value)} /></Field><Field label="Tagline (optional)"><input className="input-field" placeholder="Compassionate care, clearly coordinated" value={form.tagline} onChange={(event) => set('tagline', event.target.value)} /></Field></div>}{step === 2 && <div className="space-y-5"><Field label="Facility logo (optional)"><input className="block w-full text-sm" type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" onChange={(event) => set('logo', event.target.files?.[0] || null)} /><p className="mt-1 text-xs text-slate-500">PNG, JPEG, WebP, or SVG; up to 2 MiB.</p></Field>{preview && <img src={preview} alt="Logo preview" className="h-20 w-20 rounded-xl border border-slate-200 object-contain p-1" />}<Field label="Primary colour"><div className="flex gap-3"><input aria-label="Primary colour picker" type="color" value={form.primary_color} onChange={(event) => set('primary_color', event.target.value.toUpperCase())} className="h-11 w-14 rounded border border-slate-300 p-1" /><input className="input-field" value={form.primary_color} onChange={(event) => set('primary_color', event.target.value.toUpperCase())} pattern="^#[0-9A-Fa-f]{6}$" /></div></Field></div>}{step === 3 && <div className="space-y-4"><p className="text-sm text-slate-600">Invite your first team member now, or skip this optional step.</p><Field label="Staff email"><input type="email" className="input-field" value={form.invite_email} onChange={(event) => set('invite_email', event.target.value)} /></Field><Field label="Role"><select className="input-field" value={form.invite_role} onChange={(event) => set('invite_role', event.target.value)}><option>Clinician</option><option>Reception</option><option>Billing</option><option>Staff Member</option></select></Field></div>}{step === 4 && <div className="space-y-4 rounded-xl bg-slate-50 p-5 text-sm"><Row label="Facility" value={form.company_name} /><Row label="Tagline" value={form.tagline || 'Not set'} /><Row label="Primary colour" value={form.primary_color} swatch /><Row label="Logo" value={form.logo?.name || (preview ? 'Current logo' : 'Not set')} /><Row label="First invitation" value={form.invite_email || 'Skipped'} /></div>}</div><div className="mt-8 flex justify-between gap-3">{step > 1 ? <button className="btn-secondary" onClick={() => setStep((current) => current - 1)}>Back</button> : <span />}{step < 4 ? <button className="btn-primary" onClick={next}>Continue</button> : <button className="btn-primary" disabled={submitting} onClick={submit}>{submitting ? 'Saving…' : 'Finish setup'}</button>}</div></section></main>;
}

function Field({ label, children }: { label: string; children: ReactNode }) { return <label className="block"><span className="form-label">{label}</span>{children}</label>; }
function Row({ label, value, swatch = false }: { label: string; value: string; swatch?: boolean }) { return <div className="flex items-center justify-between gap-4"><span className="text-slate-500">{label}</span><span className="flex items-center gap-2 font-semibold text-slate-800">{swatch && <span style={{ backgroundColor: value }} className="h-4 w-4 rounded-full border border-slate-200" />}{value}</span></div>; }
function getApiError(data: unknown): string | null { if (!data || typeof data !== 'object') return null; const value = Object.values(data as Record<string, unknown>)[0]; return typeof value === 'string' ? value : Array.isArray(value) && typeof value[0] === 'string' ? value[0] : null; }
