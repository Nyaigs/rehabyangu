const roleLabels: Record<string, string> = {
  super_admin: 'Platform Administrator', rehab_admin: 'Workspace Administrator',
  psychiatrist: 'Psychiatrist', clinical_officer: 'Clinical Officer', nurse: 'Nurse',
  counselor: 'Counselor', pharmacist: 'Pharmacist', receptionist: 'Receptionist',
  accountant: 'Accountant', store_manager: 'Store Manager', hr_manager: 'HR Manager', cook: 'Cook', other: 'Staff Member',
};

export function displayRole(user?: { is_rehab_admin?: boolean; role?: string | null; is_superuser?: boolean } | null) {
  if (user?.is_superuser) return roleLabels.super_admin;
  if (user?.is_rehab_admin) return roleLabels.rehab_admin;
  return roleLabels[user?.role || 'other'] || 'Staff Member';
}
