import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';
import { Button } from '../components/ui/Button';
import { Modal } from '../components/ui/Modal';
import { Field } from '../components/ui/FormFields';
import { Table } from '../components/ui/Table';
import { Badge } from '../components/ui/Badge';
import { Checkbox } from '../components/ui/Checkbox';

function AddMedication({ close }: { close: () => void }) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ name: '', strength: '', form: '', category: '', is_controlled_substance: false });
  const save = useMutation({ mutationFn: () => api.post('/medications/', form), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['medications'] }); close(); } });
  return <Modal open onOpenChange={open => !open && close()} title="Add medication"><form className="space-y-4" onSubmit={event => { event.preventDefault(); save.mutate(); }}><div className="grid gap-4 sm:grid-cols-2"><Field label="Medication name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required /><Field label="Strength" value={form.strength} onChange={e => setForm({ ...form, strength: e.target.value })} required /><Field label="Form" value={form.form} onChange={e => setForm({ ...form, form: e.target.value })} required /><Field label="Category" value={form.category} onChange={e => setForm({ ...form, category: e.target.value })} /></div><Checkbox label="Controlled substance" checked={form.is_controlled_substance} onChange={e => setForm({ ...form, is_controlled_substance: e.target.checked })} /><div className="flex justify-end gap-3"><Button className="w-auto" variant="secondary" type="button" onClick={close}>Cancel</Button><Button className="w-auto" isLoading={save.isPending}>Add medication</Button></div></form></Modal>;
}

export default function Medications() {
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<'catalog' | 'prescriptions'>('catalog');
  const medications = useQuery({ queryKey: ['medications'], queryFn: async () => (await api.get('/medications/')).data });
  const prescriptions = useQuery({ queryKey: ['all-prescriptions'], queryFn: async () => (await api.get('/prescriptions/')).data });
  return <div className="space-y-6"><div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center"><div><h1 className="text-page-title text-secondary-800">Medications</h1><p className="text-body text-secondary-500">Medication catalog and current prescriptions.</p></div>{tab === 'catalog' && <Button className="w-auto" onClick={() => setOpen(true)}>Add medication</Button>}</div><div className="flex gap-2 border-b border-secondary-200"><Button className="w-auto rounded-b-none px-4 py-2" variant={tab === 'catalog' ? 'primary' : 'secondary'} onClick={() => setTab('catalog')}>Medication catalog</Button><Button className="w-auto rounded-b-none px-4 py-2" variant={tab === 'prescriptions' ? 'primary' : 'secondary'} onClick={() => setTab('prescriptions')}>Prescriptions</Button></div>{tab === 'catalog' ? <section className="space-y-3"><h2 className="text-section-title text-secondary-800">Medication catalog</h2><Table><thead><tr><th>Name</th><th>Strength</th><th>Form</th><th>Category</th><th>Control</th></tr></thead><tbody>{medications.data?.map((m: any) => <tr key={m.id}><td className="font-medium">{m.name}</td><td>{m.strength}</td><td>{m.form}</td><td>{m.category || '—'}</td><td>{m.is_controlled_substance && <Badge tone="warning">Controlled</Badge>}</td></tr>)}</tbody></Table></section> : <section className="space-y-3"><h2 className="text-section-title text-secondary-800">Prescriptions</h2><p className="text-body text-secondary-500">Create prescriptions from the patient record, where the clinical context is visible.</p><Table><thead><tr><th>Patient</th><th>Medication</th><th>Dose / frequency</th><th>Duration</th><th>Start</th><th>Status</th></tr></thead><tbody>{prescriptions.data?.map((p: any) => <tr key={p.id}><td>{p.patient_name}</td><td>{p.medication_name}</td><td>{p.dose} · {p.frequency}</td><td>{p.duration_days} days</td><td>{new Date(p.start_at).toLocaleDateString()}</td><td><Badge tone={p.status === 'active' ? 'success' : 'neutral'}>{p.status}</Badge></td></tr>)}</tbody></Table></section>}{open && <AddMedication close={() => setOpen(false)} />}</div>;
}
