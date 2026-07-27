import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import api from '../api/client';

const appointmentSchema = z.object({
  patient: z.number().min(1, 'Patient is required'),
  clinician: z.number().min(1, 'Clinician is required'),
  start_time: z.string().min(1, 'Start time is required'),
  end_time: z.string().min(1, 'End time is required'),
  notes: z.string().optional(),
});

type AppointmentFormInputs = z.infer<typeof appointmentSchema>;

interface Props {
  onClose: () => void;
}

const AppointmentForm: React.FC<Props> = ({ onClose }) => {
  const queryClient = useQueryClient();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<AppointmentFormInputs>({
    resolver: zodResolver(appointmentSchema),
  });

  const { data: patients } = useQuery({
    queryKey: ['patients'],
    queryFn: () => api.get('/patients/').then(res => res.data),
  });

  const { data: clinicians } = useQuery({
    queryKey: ['users'],
    queryFn: () => api.get('/users/').then(res => res.data),
  });

  const mutation = useMutation({
    mutationFn: (data: AppointmentFormInputs) => api.post('/appointments/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      onClose();
    },
  });

  const onSubmit = (data: AppointmentFormInputs) => {
    mutation.mutate(data);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Book Appointment</h2>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium">Patient *</label>
              <select {...register('patient', { valueAsNumber: true })} className="w-full border rounded px-3 py-2">
                <option value="">Select Patient</option>
                {patients?.map((p: any) => (
                  <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
                ))}
              </select>
              {errors.patient && <p className="text-red-500 text-sm">{errors.patient.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Clinician *</label>
              <select {...register('clinician', { valueAsNumber: true })} className="w-full border rounded px-3 py-2">
                <option value="">Select Clinician</option>
                {clinicians?.map((c: any) => (
                  <option key={c.id} value={c.id}>{c.first_name || c.username}</option>
                ))}
              </select>
              {errors.clinician && <p className="text-red-500 text-sm">{errors.clinician.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Start Time *</label>
              <input type="datetime-local" {...register('start_time')} className="w-full border rounded px-3 py-2" />
              {errors.start_time && <p className="text-red-500 text-sm">{errors.start_time.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">End Time *</label>
              <input type="datetime-local" {...register('end_time')} className="w-full border rounded px-3 py-2" />
              {errors.end_time && <p className="text-red-500 text-sm">{errors.end_time.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Notes</label>
              <textarea {...register('notes')} className="w-full border rounded px-3 py-2" rows={2} />
            </div>
            <div className="flex gap-2 pt-2">
              <button type="submit" disabled={isSubmitting} className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
                {isSubmitting ? 'Booking...' : 'Book Appointment'}
              </button>
              <button type="button" onClick={onClose} className="flex-1 bg-gray-300 text-gray-700 py-2 rounded hover:bg-gray-400">
                Cancel
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AppointmentForm;
