import { useAuth } from '../context/AuthContext';

/** Uses the same effective permissions returned by the API/HasPermission. */
export function usePermission(codename: string) {
  const { permissions, isSuperAdmin } = useAuth();
  return isSuperAdmin || permissions.includes(codename);
}
