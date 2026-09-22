import { useState } from 'react';
import { PlusIcon } from '@heroicons/react/24/outline';
import { usePatientNotes } from '../hooks/usePatientNotes';
import AddNoteModal from './AddNoteModal';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { EmptyState } from './EmptyState';
import { ErrorBanner } from './ErrorBanner';
import { SkeletonCard } from './Skeleton';
import { usePermission } from '../hooks/usePermission';

const sections = [['S', 'Subjective', 'subjective'], ['O', 'Objective', 'objective'], ['A', 'Assessment', 'assessment'], ['P', 'Plan', 'plan']] as const;
export default function PatientNotes({ patientId }: { patientId: number }) {
  const [open, setOpen] = useState(false); const canWrite = usePermission('clinical.write') || usePermission('clinicalnote:create');
  const notes = usePatientNotes(patientId);
  if (notes.isLoading) return <SkeletonCard count={2} />;
  if (notes.error) return <ErrorBanner>We could not load clinical notes. Try again shortly.</ErrorBanner>;
  return <div className="space-y-4"><div className="flex items-center justify-between"><div><h2 className="font-semibold text-secondary-800">Clinical notes</h2><p className="text-xs text-secondary-500">Append-only SOAP documentation</p></div>{canWrite && <Button className="w-auto py-2 text-sm" onClick={() => setOpen(true)}><PlusIcon className="h-4 w-4" />Add note</Button>}</div>{!notes.data?.length ? <EmptyState title="No clinical notes" description="Document the patient’s care with a SOAP note." iconType="documents" actionLabel={canWrite ? 'Add note' : undefined} onAction={canWrite ? () => setOpen(true) : undefined} /> : <div className="space-y-3">{notes.data.map((note: any) => <article key={note.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-card"><div className="flex flex-wrap items-center justify-between gap-2"><div><p className="font-medium text-secondary-800">{note.author_name || note.clinician_name || 'Clinical team'}</p><p className="text-xs text-secondary-500">{new Date(note.date).toLocaleString()}</p></div><Badge tone="info">SOAP v{note.version || 1}</Badge></div><div className="mt-4 grid gap-3 lg:grid-cols-2">{sections.map(([letter, label, key]) => <section key={key} className="rounded-lg bg-secondary-50 p-3"><h3 className="text-xs font-bold uppercase tracking-wide text-primary">{letter} — {label}</h3><p className="mt-1 whitespace-pre-wrap text-sm text-secondary-700">{note[key] || '—'}</p></section>)}</div></article>)}</div>}{open && <AddNoteModal patientId={patientId} onClose={() => setOpen(false)} />}</div>;
}
