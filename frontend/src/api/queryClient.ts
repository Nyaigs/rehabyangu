import { QueryClient } from '@tanstack/react-query';

/** Shared cache policy for API-backed screens. */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (failureCount, error: any) => {
        const status = error?.response?.status;
        return !status || status >= 500 ? failureCount < 2 : false;
      },
      refetchOnWindowFocus: false,
    },
    mutations: { retry: false },
  },
});
