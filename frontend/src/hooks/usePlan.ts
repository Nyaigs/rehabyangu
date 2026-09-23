import { useQuery } from '@tanstack/react-query';
import api from '../api/client';

export function usePlan() {
  const { data, isLoading } = useQuery({
    queryKey: ['tenant-plan'],
    queryFn: async () => (await api.get('/tenant-plan/')).data,
    retry: false,
  });
  return { plan: data?.plan ?? null, features: data?.features ?? {}, userCount: data?.user_count ?? 0, maxUsers: data?.max_users ?? null, isPlatformAdmin: data?.platform_admin ?? false, isLoading };
}
