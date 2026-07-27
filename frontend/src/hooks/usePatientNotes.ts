import { useQuery } from '@tanstack/react-query';
import api from '../api/client';

export function usePatientNotes(patientId: number) {
  return useQuery({
    queryKey: ['notes', patientId],
    queryFn: () => api.get(`/clinical-notes/?patient=${patientId}`).then(res => res.data),
    enabled: !!patientId,
  });
}
