import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '../components/ui/Button';
import { UsersIcon, CalendarDaysIcon, CreditCardIcon, ArrowUpIcon, ArrowRightIcon, ExclamationTriangleIcon, HeartIcon, ClipboardDocumentCheckIcon, UserPlusIcon } from '@heroicons/react/24/outline';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import api from '../api/client';
import { ErrorBanner } from '../components/ErrorBanner';
import { SkeletonCard } from '../components/Skeleton';

const fetchStats = async () => {
  return (await api.get('/dashboard/stats/')).data;
};

const trendData = [
  { month: 'Jan', patients: 34 }, { month: 'Feb', patients: 41 }, { month: 'Mar', patients: 37 },
  { month: 'Apr', patients: 48 }, { month: 'May', patients: 53 }, { month: 'Jun', patients: 61 }, { month: 'Jul', patients: 58 },
];

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data, isLoading, isError, refetch } = useQuery({ queryKey: ['dashboard-stats'], queryFn: fetchStats, refetchInterval: 30000 });
  const stats = [
    { label: 'Patients in care', value: data?.total_patients ?? 0, note: `${data?.active_patients ?? 0} active admissions`, icon: UsersIcon, tone: 'bg-blue-50 text-blue-600' },
    { label: 'Active admissions', value: data?.active_patients ?? 0, note: `${data?.staff_count ?? 0} active staff`, icon: HeartIcon, tone: 'bg-emerald-50 text-emerald-600' },
    { label: 'Reviews today', value: data?.appointments_today ?? 0, note: 'Scheduled appointments', icon: CalendarDaysIcon, tone: 'bg-amber-50 text-amber-600' },
    { label: 'Open invoice value', value: `KES ${Number(data?.outstanding_invoice_value ?? 0).toLocaleString('en-KE', { maximumFractionDigits: 0 })}`, note: 'Across issued invoices', icon: CreditCardIcon, tone: 'bg-violet-50 text-violet-600' },
  ];

  return <div className="mx-auto max-w-7xl space-y-7">
    <section className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div><p className="mb-1 text-sm font-medium text-[#237a67]">Tuesday, 5 August</p><h1 className="text-3xl font-bold tracking-tight text-slate-900">Good morning, {data ? 'welcome back' : 'care team'}.</h1><p className="mt-2 text-sm text-slate-500">Here’s what needs your attention at the clinic today.</p></div>
      <div className="flex gap-2"><Button variant="secondary" onClick={() => navigate({ to: '/reports' })} className="w-auto border-slate-200 bg-white px-3.5 py-2 text-sm">View reports <ArrowRightIcon className="ml-1.5 h-3.5 w-3.5" /></Button><Button onClick={() => navigate({ to: '/admissions' })} className="w-auto bg-[#17614f] px-3.5 py-2 text-sm hover:bg-[#104c3e]"><UserPlusIcon className="mr-1.5 h-4 w-4" />New admission</Button></div>
    </section>

    {isError && <ErrorBanner onRetry={() => refetch()}>We could not load the clinic summary. Please try again.</ErrorBanner>}

    <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {isLoading ? <SkeletonCard count={4} className="min-h-[148px]" /> : stats.map((stat) => <Card key={stat.label} className="border-slate-200/80 bg-white shadow-[0_2px_8px_rgba(15,46,61,0.04)]"><CardContent className="p-5"><div className="flex items-start justify-between"><div><p className="text-sm font-medium text-slate-500">{stat.label}</p><p className="mt-2 font-numeric text-2xl font-bold tracking-tight text-slate-900">{stat.value}</p></div><div className={`grid h-10 w-10 place-items-center rounded-xl ${stat.tone}`}><stat.icon className="h-5 w-5" /></div></div><p className="mt-4 flex items-center gap-1 text-xs text-slate-500"><ArrowUpIcon className="h-3.5 w-3.5 text-[#237a67]" /><span className="font-medium text-[#237a67]">{stat.note.split(' ')[0]}</span> {stat.note.substring(stat.note.indexOf(' ') + 1)}</p></CardContent></Card>)}
    </section>

    <section className="grid grid-cols-1 gap-5 xl:grid-cols-3">
      <Card className="border-slate-200/80 bg-white shadow-[0_2px_8px_rgba(15,46,61,0.04)] xl:col-span-2"><CardContent className="p-5 sm:p-6"><div className="mb-6 flex items-start justify-between"><div><h2 className="font-semibold text-slate-800">Patient flow</h2><p className="mt-1 text-sm text-slate-500">New admissions over the last seven months</p></div><div className="rounded-lg bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-[#237a67]">+9.4%</div></div><div className="h-64"><ResponsiveContainer width="100%" height="100%"><AreaChart data={trendData} margin={{ left: -18, right: 4, top: 5 }}><defs><linearGradient id="patient-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#3fa781" stopOpacity={0.28} /><stop offset="100%" stopColor="#3fa781" stopOpacity={0.01} /></linearGradient></defs><CartesianGrid vertical={false} stroke="#e8eeeb" /><XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} dy={10} /><YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} /><Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #e2e8f0', boxShadow: '0 8px 20px rgba(15,46,61,.08)' }} /><Area type="monotone" dataKey="patients" name="Admissions" stroke="#237a67" strokeWidth={2.5} fill="url(#patient-fill)" /></AreaChart></ResponsiveContainer></div></CardContent></Card>
      <Card className="border-slate-200/80 bg-white shadow-[0_2px_8px_rgba(15,46,61,0.04)]"><CardContent className="p-5 sm:p-6"><div className="flex items-start justify-between"><div><h2 className="font-semibold text-slate-800">Today’s priorities</h2><p className="mt-1 text-sm text-slate-500">Items requiring review</p></div><span className="grid h-8 w-8 place-items-center rounded-lg bg-amber-50 text-amber-600"><ExclamationTriangleIcon className="h-5 w-5" /></span></div><div className="mt-5 space-y-1"><Priority onClick={() => navigate({ to: '/clinical-notes' })} tone="amber" title="3 medication reviews due" detail="Clinical review required today" /><Priority onClick={() => navigate({ to: '/pending-discharges' })} tone="rose" title="2 pending discharges" detail="Awaiting final sign-off" /><Priority onClick={() => navigate({ to: '/appointments' })} tone="blue" title="5 upcoming appointments" detail="First appointment at 09:30" /></div><button onClick={() => navigate({ to: '/appointments' })} className="mt-5 flex w-full items-center justify-center gap-1 rounded-lg border border-slate-200 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-50">Open task centre <ArrowRightIcon className="h-3.5 w-3.5" /></button></CardContent></Card>
    </section>

    <section className="grid grid-cols-1 gap-5 lg:grid-cols-2"><Card className="border-slate-200/80 bg-white shadow-[0_2px_8px_rgba(15,46,61,0.04)]"><CardContent className="p-5 sm:p-6"><div className="mb-4 flex items-center justify-between"><div><h2 className="font-semibold text-slate-800">Upcoming reviews</h2><p className="mt-1 text-sm text-slate-500">Patients scheduled for clinical follow-up</p></div><ClipboardDocumentCheckIcon className="h-5 w-5 text-[#237a67]" /></div><div className="divide-y divide-slate-100"><Review initials="AM" name="Amina Mwangi" type="Clinical review" time="09:30" /><Review initials="JO" name="John Otieno" type="Treatment plan review" time="11:00" /><Review initials="NK" name="Naomi Kilonzo" type="Counselling session" time="14:30" /></div></CardContent></Card><Card className="border-slate-200/80 bg-[#173f52] text-white shadow-[0_2px_8px_rgba(15,46,61,0.08)]"><CardContent className="flex h-full flex-col justify-between p-6"><div><p className="text-xs font-semibold uppercase tracking-[0.14em] text-emerald-300">Care at a glance</p><h2 className="mt-3 text-xl font-semibold tracking-tight">Every record, one calm workspace.</h2><p className="mt-2 max-w-md text-sm leading-6 text-slate-300">Keep patients, care plans, and clinic operations coordinated throughout the day.</p></div><div className="mt-7 flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-xl bg-white/10"><HeartIcon className="h-5 w-5 text-emerald-300" /></div><p className="text-xs text-slate-300">Data updates automatically every 30 seconds.</p></div></CardContent></Card></section>
  </div>;
};

function Priority({ tone, title, detail, onClick }: { tone: 'amber' | 'rose' | 'blue'; title: string; detail: string; onClick: () => void }) { const styles = { amber: 'bg-amber-100 text-amber-600', rose: 'bg-rose-100 text-rose-600', blue: 'bg-blue-100 text-blue-600' }; return <button onClick={onClick} className="flex w-full items-center gap-3 rounded-xl p-2 text-left transition hover:bg-slate-50"><span className={`h-2 w-2 shrink-0 rounded-full ${styles[tone]}`} /><span className="min-w-0 flex-1"><span className="block text-sm font-medium text-slate-700">{title}</span><span className="block text-xs text-slate-500">{detail}</span></span><ArrowRightIcon className="h-4 w-4 text-slate-300" /></button>; }
function Review({ initials, name, type, time }: { initials: string; name: string; type: string; time: string }) { return <div className="flex items-center gap-3 py-3"><div className="grid h-9 w-9 place-items-center rounded-full bg-[#e6f4ee] text-[11px] font-bold text-[#237a67]">{initials}</div><div className="min-w-0 flex-1"><p className="text-sm font-semibold text-slate-700">{name}</p><p className="text-xs text-slate-500">{type}</p></div><p className="text-xs font-semibold text-slate-500">{time}</p></div>; }
export default Dashboard;
