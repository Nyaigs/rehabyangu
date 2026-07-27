import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';

const patientSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  date_of_birth: z.string().min(1, 'Date of birth is required'),
  gender: z.enum(['M', 'F', 'O']),
  phone: z.string().min(1, 'Phone is required'),
  email: z.string().email('Invalid email').optional(),
  address: z.string().optional(),
  emergency_contact_name: z.string().optional(),
  emergency_contact_phone: z.string().optional(),
  referring_doctor: z.string().optional(),
  notes: z.string().optional(),
});

type PatientFormInputs = z.infer<typeof patientSchema>;

interface Props {
  onClose: () => void;
}

const PatientForm: React.FC<Props> = ({ onClose }) => {
  const queryClient = useQueryClient();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<PatientFormInputs>({
    resolver: zodResolver(patientSchema),
  });

  const mutation = useMutation({
    mutationFn: (data: PatientFormInputs) => api.post('/patients/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] });
      onClose();
    },
  });

  const onSubmit = (data: PatientFormInputs) => {
    mutation.mutate(data);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Add New Patient</h2>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium">First Name *</label>
              <input {...register('first_name')} className="w-full border rounded px-3 py-2" />
              {errors.first_name && <p className="text-red-500 text-sm">{errors.first_name.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Last Name *</label>
              <input {...register('last_name')} className="w-full border rounded px-3 py-2" />
              {errors.last_name && <p className="text-red-500 text-sm">{errors.last_name.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Date of Birth *</label>
              <input type="date" {...register('date_of_birth')} className="w-full border rounded px-3 py-2" />
              {errors.date_of_birth && <p className="text-red-500 text-sm">{errors.date_of_birth.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Gender *</label>
              <select {...register('gender')} className="w-full border rounded px-3 py-2">
                <option value="">Select</option>
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="O">Other</option>
              </select>
              {errors.gender && <p className="text-red-500 text-sm">{errors.gender.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Phone *</label>
              <input {...register('phone')} className="w-full border rounded px-3 py-2" />
              {errors.phone && <p className="text-red-500 text-sm">{errors.phone.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Email</label>
              <input type="email" {...register('email')} className="w-full border rounded px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium">Address</label>
              <input {...register('address')} className="w-full border rounded px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium">Emergency Contact Name</label>
              <input {...register('emergency_contact_name')} className="w-full border rounded px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium">Emergency Contact Phone</label>
              <input {...register('emergency_contact_phone')} className="w-full border rounded px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium">Referring Doctor</label>
              <input {...register('referring_doctor')} className="w-full border rounded px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium">Notes</label>
              <textarea {...register('notes')} className="w-full border rounded px-3 py-2" rows={3} />
            </div>
            <div className="flex gap-2 pt-2">
              <button type="submit" disabled={isSubmitting} className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
                {isSubmitting ? 'Saving...' : 'Save Patient'}
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

export default PatientForm;
