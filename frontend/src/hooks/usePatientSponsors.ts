import { useQuery } from '@tanstack/react-query';
import api from '../api/client';

export function usePatientSponsors(patientId: number) {
  return useQuery({
    queryKey: ['sponsors', patientId],
    queryFn: () => api.get(`/sponsors/?patient=${patientId}`).then(res => res.data),
    enabled: !!patientId,
  });
}
