import { useState } from 'react';
import { useNavigate, useSearch } from '@tanstack/react-router';
import api, { normalizeTenantSlug } from '../api/client';
import { ErrorBanner } from '../components/ErrorBanner';

export default function InvitationAccept() {
  const navigate = useNavigate();
  const search = useSearch({ strict: false }) as { tenant?: string; token?: string };
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [complete, setComplete] = useState(false);
  const [busy, setBusy] = useState(false);
  const tenant = normalizeTenantSlug(search.tenant);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault(); setError('');
    if (!tenant || !search.token) return setError('This invitation link is incomplete. Ask your administrator for a new invitation.');
    if (password.length < 12) return setError('Use a password with at least 12 characters.');
    if (password !== confirmPassword) return setError('Passwords do not match.');
    setBusy(true);
    try { await api.post('/invitations/accept/', { tenant, token: search.token, username, password }); setComplete(true); }
    catch (requestError: any) { setError(requestError.response?.data?.error || 'We could not activate this invitation.'); }
    finally { setBusy(false); }
  };

  return <main className="grid min-h-screen place-items-center bg-[#f3f7f6] p-6"><section className="w-full max-w-md rounded-2xl bg-white p-7 shadow-sm ring-1 ring-slate-200"><div className="mb-6"><span className="grid h-10 w-10 place-items-center rounded-xl bg-[#17614f] text-lg font-bold text-white">R</span><h1 className="mt-4 text-2xl font-bold text-secondary-800">Activate your account</h1><p className="mt-1 text-sm text-secondary-500">Create your sign-in details for this RehabYangu workspace.</p></div>{complete ? <div className="space-y-4"><p className="rounded-lg bg-emerald-50 p-4 text-sm text-emerald-800">Your account is ready. You can now sign in.</p><button className="btn-primary w-full" onClick={() => navigate({ to: '/login' })}>Go to sign in</button></div> : <form className="space-y-4" onSubmit={submit}>{error && <ErrorBanner>{error}</ErrorBanner>}<label className="block"><span className="form-label">Username (optional)</span><input className="input-field" value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" /></label><label className="block"><span className="form-label">Password</span><input required type="password" className="input-field" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="new-password" /></label><label className="block"><span className="form-label">Confirm password</span><input required type="password" className="input-field" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} autoComplete="new-password" /></label><button className="btn-primary w-full" disabled={busy}>{busy ? 'Activating…' : 'Activate account'}</button></form>}</section></main>;
}
