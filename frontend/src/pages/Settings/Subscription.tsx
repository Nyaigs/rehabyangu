import { CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { usePlan } from '../../hooks/usePlan';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';

const money = (value?: string) => new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', maximumFractionDigits: 0 }).format(Number(value || 0));
export default function Subscription() {
  const { plan, features, userCount, maxUsers, isLoading } = usePlan();
  if (isLoading) return <div className="animate-pulse rounded-card bg-secondary-100 p-8">Loading subscription…</div>;
  return <div className="mx-auto max-w-3xl space-y-5"><div><h1 className="text-page-title text-ink-primary">Subscription</h1><p className="mt-1 text-sm text-ink-secondary">Review your current plan and included features.</p></div><Card><CardHeader><CardTitle>{plan?.name || 'No plan assigned'}</CardTitle></CardHeader><CardContent><p className="text-2xl font-semibold text-ink-primary">{money(plan?.price_monthly)}<span className="text-sm font-normal text-ink-secondary"> / month</span></p><p className="mt-2 text-sm text-ink-secondary">Users: {userCount} / {maxUsers ?? 'Unlimited'}</p><h2 className="mt-6 font-semibold text-ink-primary">Plan features</h2><ul className="mt-3 grid gap-2 sm:grid-cols-2">{Object.entries(features).map(([name, enabled]) => <li key={name} className="flex items-center gap-2 text-sm capitalize text-ink-primary">{enabled ? <CheckIcon className="h-4 w-4 text-primary" /> : <XMarkIcon className="h-4 w-4 text-ink-muted" />}{name.replace(/_/g, ' ')}</li>)}</ul><p className="mt-6 text-sm text-ink-secondary">To change your plan, contact WeiraLynk at <a className="font-medium text-primary underline" href="mailto:hello@weiralynk.com">hello@weiralynk.com</a>.</p></CardContent></Card></div>;
}
