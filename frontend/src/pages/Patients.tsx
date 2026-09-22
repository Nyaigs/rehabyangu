import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Bars3Icon, MagnifyingGlassIcon, Squares2X2Icon, TableCellsIcon, UserPlusIcon } from '@heroicons/react/24/outline';
import api from '../api/client';
import PatientForm from '../components/PatientForm';
import { EmptyState } from '../components/EmptyState';
import { SkeletonPatientCard } from '../components/Skeleton';
import { ErrorBanner } from '../components/ErrorBanner';
import { usePermission } from '../hooks/usePermission';

type ViewMode = 'table' | 'list' | 'cards';
type Patient = { id: number; first_name: string; last_name: string; patient_id?: string; date_of_birth?: string; gender?: string; care_type?: string; status?: string; intake_date?: string; phone?: string };
const filters = [['', 'All'], ['admitted', 'Admitted'], ['outpatient', 'Outpatient'], ['day_patient', 'Day Patient'], ['discharged', 'Discharged'], ['registered', 'New'], ['transferred', 'Transferred']] as const;
const statusTone = (status?: string) => status === 'active' ? 'success' : status === 'discharged' ? 'neutral' : status === 'transferred' ? 'warning' : 'info';
const statusLabel = (status?: string) => ({ active: 'Active', registered: 'New', discharged: 'Discharged', transferred: 'Transferred', inactive: 'Inactive' }[status || ''] || status || '—');
const careLabel = (care?: string) => ({ inpatient: 'Inpatient', outpatient: 'Outpatient', day_patient: 'Day patient', new_referral: 'Referral' }[care || ''] || care || '—');
const age = (value?: string) => value ? Math.floor((Date.now() - new Date(value).getTime()) / 31557600000) : null;
const patientName = (p: Patient) => `${p.first_name} ${p.last_name}`;
const displayId = (p: Patient) => p.patient_id || `PT-${p.id}`;
const date = (value?: string) => value ? new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(value)) : '—';
function preferredView(): ViewMode { try { const value = localStorage.getItem('rehabyangu.patientView'); return value === 'table' || value === 'list' || value === 'cards' ? value : 'table'; } catch { return 'table'; } }

function PatientIdentity({ patient }: { patient: Patient }) { return <div className="flex min-w-0 items-center gap-3"><span aria-hidden="true" className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-primary/10 text-xs font-bold text-primary">{patient.first_name?.[0]}{patient.last_name?.[0]}</span><div className="min-w-0"><p className="truncate text-sm font-semibold text-ink-primary">{patientName(patient)}</p><p className="font-mono text-xs text-ink-secondary">{displayId(patient)}</p></div></div>; }
function PatientAction({ patient }: { patient: Patient }) { return <Link to="/patients/$id" params={{ id: String(patient.id) }}><Button size="sm" variant="secondary" className="w-auto whitespace-nowrap">View record</Button></Link>; }
function ViewButton({ active, label, onClick, children }: { active: boolean; label: string; onClick: () => void; children: React.ReactNode }) { return <button type="button" title={label} aria-label={label} aria-pressed={active} onClick={onClick} className={`grid h-8 w-8 place-items-center rounded-sm transition ${active ? 'bg-primary text-white shadow-sm' : 'text-ink-secondary hover:bg-secondary-100'}`}>{children}</button>; }

export default function Patients() {
  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState(() => new URLSearchParams(window.location.search).get('search') || '');
  const [debouncedSearch, setDebouncedSearch] = useState(search);
  const [filter, setFilter] = useState(''); const [page, setPage] = useState(1); const [view, setView] = useState<ViewMode>(preferredView);
  const canCreate = usePermission('patient:create') || usePermission('patient.write');
  useEffect(() => { const timer = window.setTimeout(() => { setDebouncedSearch(search); setPage(1); const url = new URL(window.location.href); search ? url.searchParams.set('search', search) : url.searchParams.delete('search'); window.history.replaceState({}, '', url); }, 300); return () => clearTimeout(timer); }, [search]);
  useEffect(() => { try { localStorage.setItem('rehabyangu.patientView', view); } catch { /* Preference storage is optional. */ } }, [view]);
  const { data, isLoading, isFetching, error, refetch } = useQuery({ queryKey: ['patients', debouncedSearch, filter, page], queryFn: ({ signal }) => api.get('/patients/', { params: { search: debouncedSearch || undefined, filter: filter || undefined, page }, signal }).then(({ data }) => data) });
  const patients: Patient[] = data?.results || [];
  const clear = () => { setSearch(''); setDebouncedSearch(''); setFilter(''); setPage(1); };
  return <div className="space-y-4">
    <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center"><div><h1 className="text-xl font-bold text-ink-primary">Patients</h1><p className="text-xs text-ink-secondary">Demographics, care status, and registration records</p></div>{canCreate && <Button className="w-auto px-3 py-2 text-sm" onClick={() => setShowForm(true)}><UserPlusIcon className="mr-1.5 h-3.5 w-3.5" />Add patient</Button>}</div>
    <div className="flex flex-col gap-3 rounded-card border border-border bg-surface p-3 sm:flex-row sm:items-center"><div className="relative min-w-0 flex-1"><MagnifyingGlassIcon className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink-muted" /><Input aria-label="Search patients" placeholder="Search name, patient ID, or phone" className="h-9 pl-9 pr-20 text-sm" value={search} onChange={(event) => setSearch(event.target.value)} />{isFetching && !isLoading && <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-ink-secondary">Searching…</span>}</div><div className="inline-flex self-start rounded-btn border border-border bg-background p-0.5" aria-label="Patient view"><ViewButton active={view === 'table'} label="Table view" onClick={() => setView('table')}><TableCellsIcon className="h-4 w-4" /></ViewButton><ViewButton active={view === 'list'} label="Compact list view" onClick={() => setView('list')}><Bars3Icon className="h-4 w-4" /></ViewButton><ViewButton active={view === 'cards'} label="Card view" onClick={() => setView('cards')}><Squares2X2Icon className="h-4 w-4" /></ViewButton></div></div>
    <div className="flex flex-wrap gap-2" aria-label="Patient workflow filters">{filters.map(([value, label]) => <Button key={value} size="sm" variant={filter === value ? 'primary' : 'secondary'} aria-pressed={filter === value} onClick={() => { setFilter(value); setPage(1); }}>{label}</Button>)}</div>
    {isLoading ? <SkeletonPatientCard count={3} /> : error ? <ErrorBanner onRetry={() => refetch()}>We could not load patients. Check your connection and try again.</ErrorBanner> : patients.length === 0 ? <EmptyState title={debouncedSearch ? 'No patients match your search.' : filter ? `No ${filters.find(([value]) => value === filter)?.[1].toLowerCase()} patients found.` : 'No patients have been registered yet.'} description={debouncedSearch || filter ? 'Try clearing your search or filters.' : 'Register a patient to begin their care journey.'} actionLabel={debouncedSearch || filter ? 'Clear search and filters' : canCreate ? 'Add patient' : undefined} onAction={debouncedSearch || filter ? clear : canCreate ? () => setShowForm(true) : undefined} iconType={debouncedSearch ? 'search' : 'users'} /> : <PatientResults patients={patients} view={view} />}
    {data?.count > patients.length && <div className="flex items-center justify-center gap-3"><Button size="sm" variant="secondary" disabled={!data.previous} onClick={() => setPage((current) => current - 1)}>Previous</Button><span className="text-xs text-ink-secondary">Page {page}</span><Button size="sm" variant="secondary" disabled={!data.next} onClick={() => setPage((current) => current + 1)}>Next</Button></div>}{showForm && <PatientForm onClose={() => setShowForm(false)} />}
  </div>;
}

function PatientResults({ patients, view }: { patients: Patient[]; view: ViewMode }) {
  if (view === 'table') return <><div className="hidden overflow-hidden rounded-card border border-border bg-surface md:block"><table className="w-full text-left"><thead className="border-b border-border bg-secondary-50 text-xs font-semibold text-ink-secondary"><tr><th className="px-4 py-3">Patient</th><th className="px-3 py-3">Age / gender</th><th className="px-3 py-3">Care type</th><th className="px-3 py-3">Status</th><th className="px-3 py-3">Registered</th><th className="px-4 py-3 text-right">Actions</th></tr></thead><tbody className="divide-y divide-border">{patients.map((p) => <tr key={p.id} className="hover:bg-secondary-50/70"><td className="px-4 py-3"><PatientIdentity patient={p} /></td><td className="px-3 py-3 text-xs text-ink-secondary">{age(p.date_of_birth) ?? '—'} · {p.gender || '—'}</td><td className="px-3 py-3 text-xs text-ink-secondary">{careLabel(p.care_type)}</td><td className="px-3 py-3"><Badge tone={statusTone(p.status) as 'success'}>{statusLabel(p.status)}</Badge></td><td className="px-3 py-3 text-xs text-ink-secondary">{date(p.intake_date)}</td><td className="px-4 py-3 text-right"><PatientAction patient={p} /></td></tr>)}</tbody></table></div><div className="md:hidden"><PatientResults patients={patients} view="list" /></div></>;
  if (view === 'list') return <div className="divide-y overflow-hidden rounded-card border border-border bg-surface">{patients.map((p) => <div key={p.id} className="flex flex-wrap items-center gap-x-5 gap-y-3 px-4 py-3"><PatientIdentity patient={p} /><div className="ml-auto flex items-center gap-3 text-xs text-ink-secondary"><span className="hidden sm:inline">{age(p.date_of_birth) ?? '—'} yrs · {p.gender || '—'} · {careLabel(p.care_type)}</span><Badge tone={statusTone(p.status) as 'success'}>{statusLabel(p.status)}</Badge><PatientAction patient={p} /></div></div>)}</div>;
  return <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">{patients.map((p) => <Card key={p.id} className="border-border shadow-none transition-shadow hover:shadow-card-hover"><CardContent className="space-y-4 p-4"><div className="flex items-start justify-between gap-3"><PatientIdentity patient={p} /><Badge tone={statusTone(p.status) as 'success'}>{statusLabel(p.status)}</Badge></div><div className="grid grid-cols-2 gap-y-2 text-xs text-ink-secondary"><span>{age(p.date_of_birth) ?? '—'} yrs · {p.gender || '—'}</span><span>Care: {careLabel(p.care_type)}</span><span className="col-span-2">Registered {date(p.intake_date)}</span></div><PatientAction patient={p} /></CardContent></Card>)}</div>;
}
