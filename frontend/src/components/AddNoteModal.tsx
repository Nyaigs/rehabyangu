import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { XMarkIcon } from '@heroicons/react/24/outline';
import api from '../api/client';
import { useToast } from '../context/ToastContext';

const noteSchema = z.object({
  subjective: z.string().min(1, 'Subjective is required'),
  objective: z.string().min(1, 'Objective is required'),
  assessment: z.string().min(1, 'Assessment is required'),
  plan: z.string().min(1, 'Plan is required'),
});

type NoteFormInputs = z.infer<typeof noteSchema>;

interface AddNoteModalProps {
  patientId: number;
  onClose: () => void;
}

const AddNoteModal: React.FC<AddNoteModalProps> = ({ patientId, onClose }) => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const { register, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm<NoteFormInputs>({
    resolver: zodResolver(noteSchema),
  });

  const mutation = useMutation({
    mutationFn: (data: NoteFormInputs) => api.post('/clinical-notes/', { ...data, patient: patientId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clinical-notes'] });
      queryClient.invalidateQueries({ queryKey: ['patient-notes', patientId] });
      toast.showToast('Note added successfully!', 'success');
      reset();
      onClose();
    },
    onError: (error: any) => {
      toast.showToast(error.response?.data?.error || 'Failed to add note', 'error');
    },
  });

  const onSubmit = (data: NoteFormInputs) => mutation.mutate(data);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content animate-scaleIn" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-lg font-semibold text-secondary-800">Add SOAP Note</h2>
          <button onClick={onClose} className="text-secondary-400 hover:text-secondary-600">
            <XMarkIcon className="w-4 h-4" />
          </button>
        </div>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <div>
              <label className="form-label">Subjective (S)</label>
              <textarea
                {...register('subjective')}
                className={`input-field ${errors.subjective ? 'input-error' : ''}`}
                rows={2}
                placeholder="Patient's reported symptoms, feelings, concerns..."
              />
              {errors.subjective && <p className="text-xs text-red-600 mt-1">{errors.subjective.message}</p>}
            </div>
            <div>
              <label className="form-label">Objective (O)</label>
              <textarea
                {...register('objective')}
                className={`input-field ${errors.objective ? 'input-error' : ''}`}
                rows={2}
                placeholder="Observable data, vitals, exam findings..."
              />
              {errors.objective && <p className="text-xs text-red-600 mt-1">{errors.objective.message}</p>}
            </div>
            <div>
              <label className="form-label">Assessment (A)</label>
              <textarea
                {...register('assessment')}
                className={`input-field ${errors.assessment ? 'input-error' : ''}`}
                rows={2}
                placeholder="Clinical judgment, diagnosis, interpretation..."
              />
              {errors.assessment && <p className="text-xs text-red-600 mt-1">{errors.assessment.message}</p>}
            </div>
            <div>
              <label className="form-label">Plan (P)</label>
              <textarea
                {...register('plan')}
                className={`input-field ${errors.plan ? 'input-error' : ''}`}
                rows={2}
                placeholder="Next steps, treatments, referrals, follow-up..."
              />
              {errors.plan && <p className="text-xs text-red-600 mt-1">{errors.plan.message}</p>}
            </div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-primary w-full justify-center"
            >
              {isSubmitting ? 'Saving...' : 'Save Note'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddNoteModal;
