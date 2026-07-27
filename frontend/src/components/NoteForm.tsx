import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';

const noteSchema = z.object({
  subjective: z.string().min(1, 'Subjective is required'),
  objective: z.string().min(1, 'Objective is required'),
  assessment: z.string().min(1, 'Assessment is required'),
  plan: z.string().min(1, 'Plan is required'),
});

type NoteFormInputs = z.infer<typeof noteSchema>;

interface Props {
  patientId: number;
  onClose: () => void;
}

const NoteForm: React.FC<Props> = ({ patientId, onClose }) => {
  const queryClient = useQueryClient();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<NoteFormInputs>({
    resolver: zodResolver(noteSchema),
  });

  const mutation = useMutation({
    mutationFn: (data: NoteFormInputs) => api.post('/clinical-notes/', { ...data, patient: patientId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes', patientId] });
      onClose();
    },
  });

  const onSubmit = (data: NoteFormInputs) => mutation.mutate(data);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Add SOAP Note</h2>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium">Subjective *</label>
              <textarea {...register('subjective')} className="w-full border rounded px-3 py-2" rows={2} />
              {errors.subjective && <p className="text-red-500 text-sm">{errors.subjective.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Objective *</label>
              <textarea {...register('objective')} className="w-full border rounded px-3 py-2" rows={2} />
              {errors.objective && <p className="text-red-500 text-sm">{errors.objective.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Assessment *</label>
              <textarea {...register('assessment')} className="w-full border rounded px-3 py-2" rows={2} />
              {errors.assessment && <p className="text-red-500 text-sm">{errors.assessment.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium">Plan *</label>
              <textarea {...register('plan')} className="w-full border rounded px-3 py-2" rows={2} />
              {errors.plan && <p className="text-red-500 text-sm">{errors.plan.message}</p>}
            </div>
            <div className="flex gap-2 pt-2">
              <button type="submit" disabled={isSubmitting} className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
                {isSubmitting ? 'Saving...' : 'Save Note'}
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

export default NoteForm;
