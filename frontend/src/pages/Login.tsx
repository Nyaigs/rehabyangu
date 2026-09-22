import React, { useEffect, useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { ArrowRightIcon, BuildingOffice2Icon, CheckCircleIcon, EyeIcon, EyeSlashIcon, LockClosedIcon, UserIcon } from '@heroicons/react/24/outline';
import api, { normalizeTenantSlug, resolveMediaUrl } from '../api/client';
import { useAuth } from '../context/AuthContext';

interface LoginBranding { company_name: string; logo_url: string | null }
const PLATFORM_WORKSPACE = 'weiraro';
const platformBranding: LoginBranding = { company_name: 'RehabYangu Platform Administration', logo_url: null };

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [tenantSlug, setTenantSlug] = useState('');
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [branding, setBranding] = useState<LoginBranding | null>(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const workspace = normalizeTenantSlug(tenantSlug);
    if (!workspace) { setBranding(null); return; }
    if (workspace === PLATFORM_WORKSPACE) { setBranding(platformBranding); return; }
    const timer = window.setTimeout(() => {
      api.get<LoginBranding>('/tenant-branding/', { headers: { 'X-Tenant': workspace } })
        .then(({ data }) => setBranding(data))
        .catch(() => setBranding(null));
    }, 350);
    return () => window.clearTimeout(timer);
  }, [tenantSlug]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const platform = await login(username.trim(), password, tenantSlug);
      navigate({ to: platform ? '/admin' : '/' });
    } catch (requestError: any) {
      setError(getErrorMessage(requestError.response?.data) || requestError.message || 'We could not sign you in. Check your details and try again.');
    } finally {
      setLoading(false);
    }
  };

  return <main className="min-h-screen bg-[#f3f7f6] p-4 text-slate-900 sm:p-6 lg:p-8">
    <div className="mx-auto grid min-h-[calc(100vh-2rem)] max-w-6xl overflow-hidden rounded-[28px] border border-slate-200/80 bg-white shadow-[0_24px_70px_rgba(15,46,61,.12)] sm:min-h-[calc(100vh-3rem)] lg:grid-cols-[1.02fr_.98fr]">
      <section className="relative hidden overflow-hidden bg-[#103d4c] p-12 text-white lg:flex lg:flex-col">
        <div className="absolute -right-32 -top-24 h-80 w-80 rounded-full bg-emerald-300/10 blur-3xl" />
        <div className="absolute -bottom-36 -left-24 h-96 w-96 rounded-full bg-sky-300/10 blur-3xl" />
        <Brand branding={branding} />
        <div className="relative my-auto max-w-md"><p className="mb-5 text-xs font-bold uppercase tracking-[.18em] text-emerald-200">Care operations, made clear</p><h1 className="text-4xl font-semibold leading-[1.15] tracking-tight">One calm, secure place for your care team.</h1><p className="mt-6 text-base leading-7 text-slate-200">Coordinate care, clinical records and daily operations with confidence—without adding complexity to the day.</p></div>
        <div className="relative flex items-center gap-3 border-t border-white/15 pt-7 text-sm text-slate-200"><span className="grid h-9 w-9 place-items-center rounded-full bg-white/10"><LockClosedIcon className="h-4 w-4 text-emerald-200" /></span><span>Protected access for authorised care teams.</span></div>
      </section>
      <section className="flex items-center justify-center px-6 py-12 sm:px-12 lg:px-16">
        <div className="w-full max-w-[390px] animate-fade-in"><div className="mb-10 lg:hidden"><Brand branding={branding} dark /></div><div className="mb-8"><p className="text-sm font-semibold text-[#17614f]">Welcome back</p><h2 className="mt-2 text-[30px] font-bold tracking-tight text-[#102c3c]">Sign in to your workspace</h2><p className="mt-3 text-[15px] leading-6 text-slate-600">Use your facility workspace and account details to continue.</p></div>
          <form onSubmit={handleSubmit} className="space-y-5">
            <Field label="Workspace" icon={<BuildingOffice2Icon className="h-4 w-4" />}><input value={tenantSlug} onChange={(event) => setTenantSlug(event.target.value)} required placeholder="e.g. serenity or weiraro" className="h-12 w-full rounded-xl border border-slate-300 bg-white pl-11 pr-3 text-[15px] font-medium text-slate-900 outline-none transition placeholder:font-normal placeholder:text-slate-400 focus:border-[#17614f] focus:ring-4 focus:ring-emerald-50" /></Field>
            {branding && <div className="-mt-2 flex items-center gap-3 rounded-xl border border-emerald-100 bg-emerald-50/60 px-3 py-2.5"><BrandMark branding={branding} small /><span className="min-w-0 text-sm font-semibold text-[#174f42]">{branding.company_name}</span><CheckCircleIcon className="ml-auto h-4 w-4 shrink-0 text-[#237a67]" /></div>}
            <Field label="Username" icon={<UserIcon className="h-4 w-4" />}><input autoComplete="username" value={username} onChange={(event) => setUsername(event.target.value)} required placeholder="Enter your username" className="h-12 w-full rounded-xl border border-slate-300 bg-white pl-11 pr-3 text-[15px] font-medium text-slate-900 outline-none transition placeholder:font-normal placeholder:text-slate-400 focus:border-[#17614f] focus:ring-4 focus:ring-emerald-50" /></Field>
            <Field label="Password" icon={<LockClosedIcon className="h-4 w-4" />}><input autoComplete="current-password" type={isPasswordVisible ? 'text' : 'password'} value={password} onChange={(event) => setPassword(event.target.value)} required placeholder="Enter your password" className="h-12 w-full rounded-xl border border-slate-300 bg-white pl-11 pr-12 text-[15px] font-medium text-slate-900 outline-none transition placeholder:font-normal placeholder:text-slate-400 focus:border-[#17614f] focus:ring-4 focus:ring-emerald-50" /><button type="button" onClick={() => setIsPasswordVisible((visible) => !visible)} aria-label={isPasswordVisible ? 'Hide password' : 'Show password'} aria-pressed={isPasswordVisible} className="absolute right-1.5 top-1/2 grid h-9 w-9 -translate-y-1/2 place-items-center rounded-lg text-slate-500 transition hover:bg-slate-100 hover:text-[#17614f]">{isPasswordVisible ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}</button></Field>
            {error && <p role="alert" className="rounded-xl border border-rose-200 bg-rose-50 px-3 py-2.5 text-sm font-medium text-rose-800">{error}</p>}
            <button disabled={loading} type="submit" className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-[#17614f] text-[15px] font-semibold text-white shadow-sm transition hover:bg-[#104c3e] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-emerald-200 disabled:cursor-not-allowed disabled:opacity-60">{loading ? 'Signing in…' : <>Sign in securely <ArrowRightIcon className="h-4 w-4" /></>}</button>
          </form><p className="mt-5 text-center text-sm text-slate-600">Forgot your password? <a className="font-semibold text-[#17614f] underline hover:text-[#104c3e]" href="mailto:admin@rehabyangu.com?subject=RehabYangu%20access%20help">Contact your administrator</a>.</p><p className="mt-4 text-center text-xs leading-5 text-slate-500">By continuing, you confirm that you are authorised to access this clinical workspace.</p>
        </div>
      </section>
    </div>
  </main>;
};

function getErrorMessage(data: unknown): string | null { if (!data || typeof data !== 'object') return null; const first = Object.values(data as Record<string, unknown>)[0]; return typeof first === 'string' ? first : Array.isArray(first) && typeof first[0] === 'string' ? first[0] : null; }
function BrandMark({ branding, small = false }: { branding?: LoginBranding | null; small?: boolean }) { const size = small ? 'h-8 w-8 rounded-lg' : 'h-10 w-10 rounded-xl'; const logoUrl = resolveMediaUrl(branding?.logo_url); return logoUrl ? <img src={logoUrl} alt={`${branding?.company_name || 'Facility'} logo`} className={`${size} shrink-0 bg-white p-1 object-contain`} /> : <div className={`grid ${size} shrink-0 place-items-center bg-[#2b9b7c] text-lg font-bold text-white shadow-lg shadow-emerald-950/20`}>R</div>; }
function Brand({ branding, dark = false }: { branding?: LoginBranding | null; dark?: boolean }) { return <div className="relative flex items-center gap-3"><BrandMark branding={branding} /><div><p className={`font-semibold tracking-tight ${dark ? 'text-slate-900' : 'text-white'}`}>{branding?.company_name || 'RehabYangu'}</p><p className="text-[10px] font-semibold uppercase tracking-[.16em] text-slate-400">Care workspace</p></div></div>; }
function Field({ label, icon, children }: { label: string; icon: React.ReactNode; children: React.ReactNode }) { return <label className="block"><span className="mb-2 block text-sm font-semibold text-slate-700">{label}</span><span className="relative block"><span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">{icon}</span>{children}</span></label>; }
export default Login;
