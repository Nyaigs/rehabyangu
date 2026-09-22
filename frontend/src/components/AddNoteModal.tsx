import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';
import { Modal } from './ui/Modal';
import { Button } from './ui/Button';
import { SelectField, TextareaField } from './ui/FormFields';
import { ErrorBanner } from './ErrorBanner';

const schema = z.object({ patient: z.coerce.number().positive('Select a patient'), subjective: z.string().min(1, 'Subjective is required'), objective: z.string().min(1, 'Objective is required'), assessment: z.string().min(1, 'Assessment is required'), plan: z.string().min(1, 'Plan is required') });
type Values = z.infer<typeof schema>;
export default function AddNoteModal({ patientId, onClose }: { patientId?: number; onClose: () => void }) {
  const client = useQueryClient(); const patients = useQuery({ queryKey: ['patients'], queryFn: async () => (await api.get('/patients/')).data, enabled: !patientId });
  const form = useForm<Values>({ resolver: zodResolver(schema) as any, defaultValues: patientId ? { patient: patientId } : undefined });
  const mutation = useMutation({ mutationFn: (values: Values) => api.post('/clinical-notes/', values), onSuccess: () => { client.invalidateQueries({ queryKey: ['clinical-notes'] }); client.invalidateQueries({ queryKey: ['patient-notes', patientId] }); onClose(); } });
  return <Modal open onOpenChange={open => !open && onClose()} title="Add SOAP note"><form className="space-y-4" onSubmit={form.handleSubmit(values => mutation.mutate(values))}>{!patientId && <SelectField label="Patient" error={form.formState.errors.patient?.message} {...form.register('patient')}><option value="">Select patient</option>{patients.data?.map((patient: any) => <option key={patient.id} value={patient.id}>{patient.first_name} {patient.last_name}</option>)}</SelectField>}<TextareaField label="S — Subjective" rows={3} placeholder="Patient's reported symptoms, concerns, and feelings" error={form.formState.errors.subjective?.message} {...form.register('subjective')} /><TextareaField label="O — Objective" rows={3} placeholder="Observed data, examination, and relevant findings" error={form.formState.errors.objective?.message} {...form.register('objective')} /><TextareaField label="A — Assessment" rows={3} placeholder="Clinical assessment and interpretation" error={form.formState.errors.assessment?.message} {...form.register('assessment')} /><TextareaField label="P — Plan" rows={3} placeholder="Care plan, referrals, and follow-up" error={form.formState.errors.plan?.message} {...form.register('plan')} />{mutation.isError && <ErrorBanner>We could not save this clinical note. Try again shortly.</ErrorBanner>}<div className="flex justify-end gap-3"><Button type="button" variant="secondary" className="w-auto" onClick={onClose}>Cancel</Button><Button className="w-auto" isLoading={mutation.isPending}>Save note</Button></div></form></Modal>;
}
