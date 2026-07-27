import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';

const sponsorSchema = z.object({
  full_name: z.string().min(1, 'Full name is required'),
  phone: z.string().min(1, 'Phone is required'),
  email: z.string().email('Invalid email').optional(),
  relationship: z.enum(['family', 'employer', 'self', 'government', 'ngo', 'other']),
  company_name: z.string().optional(),
  notes: z.string().optional(),
});

type SponsorFormInputs = z.infer<typeof sponsorSchema>;

interface Props {
  patientId: number;
  onClose: () => void;
}

const SponsorForm: React.FC<Props> = ({ patientId, onClose }) => {
  const queryClient = useQueryClient();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<SponsorFormInputs>({
    resolver: zodResolver(sponsorSchema),
  });

  const mutation = useMutation({
    mutationFn: (data: SponsorFormInputs) => api.post('/sponsors/', { ...data, patient: patientId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sponsors', patientId] });
      onClose();
    },
  });

  const onSubmit = (data: SponsorFormInputs) => mutation.mutate(data);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Add Sponsor</h2>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium">Full Name *</label>
              <input {...register('full_name')} className="w-full border rounded px-3 py-2" />
              {errors.full_name && <p className="text-red-500 text-sm">{errors.full_name.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Phone *</label>
              <input {...register('phone')} className="w-full border rounded px-3 py-2" />
              {errors.phone && <p className="text-red-500 text-sm">{errors.phone.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Email</label>
              <input type="email" {...register('email')} className="w-full border rounded px-3 py-2" />
              {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Relationship *</label>
              <select {...register('relationship')} className="w-full border rounded px-3 py-2">
                <option value="">Select</option>
                <option value="family">Family Member</option>
                <option value="employer">Employer</option>
                <option value="self">Self</option>
                <option value="government">Government</option>
                <option value="ngo">NGO</option>
                <option value="other">Other</option>
              </select>
              {errors.relationship && <p className="text-red-500 text-sm">{errors.relationship.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Company Name</label>
              <input {...register('company_name')} className="w-full border rounded px-3 py-2" />
            </div>
            <div>
              <label className="block text-sm font-medium">Notes</label>
              <textarea {...register('notes')} className="w-full border rounded px-3 py-2" rows={2} />
            </div>
            <div className="flex gap-2 pt-2">
              <button type="submit" disabled={isSubmitting} className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
                {isSubmitting ? 'Saving...' : 'Save Sponsor'}
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

export default SponsorForm;
