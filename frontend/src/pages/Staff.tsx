import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { PlusIcon, PencilSquareIcon, XMarkIcon } from '@heroicons/react/24/outline';
import api from '../api/client';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';
import { ErrorBanner } from '../components/ErrorBanner';
import { SkeletonTable } from '../components/Skeleton';
import { EmptyState } from '../components/EmptyState';

const inviteSchema = z.object({ email: z.string().email(), first_name: z.string(), last_name: z.string(), role: z.string().min(1), extra_permissions: z.array(z.string()) });
type InviteValues = z.infer<typeof inviteSchema>;
const get = async (path: string) => (await api.get(path)).data;

const Staff: React.FC = () => {
  const toast = useToast(); const queryClient = useQueryClient(); const { isRehabAdmin } = useAuth();
  const [editing, setEditing] = useState<any | null>(null); const [inviting, setInviting] = useState(false);
  const staff = useQuery({ queryKey: ['staff'], queryFn: () => get('/staff/'), enabled: isRehabAdmin });
  const permissions = useQuery({ queryKey: ['permissions'], queryFn: () => get('/permissions/'), enabled: isRehabAdmin });
  const roles = useQuery({ queryKey: ['roles'], queryFn: () => get('/roles/'), enabled: isRehabAdmin });
  const create = useMutation({ mutationFn: (body: InviteValues) => api.post('/staff/create/', { ...body, extra_permissions: [] }), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['staff'] }); setInviting(false); toast.showToast('Invitation sent. The staff member will set their password from the email link.', 'success'); }, onError: (e: any) => toast.showToast(e.response?.data?.error || 'Unable to invite staff', 'error') });
  const update = useMutation({ mutationFn: ({ id, body }: any) => api.put(`/staff/${id}/`, body), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['staff'] }); setEditing(null); toast.showToast('Staff permissions updated', 'success'); }, onError: (e: any) => toast.showToast(e.response?.data?.error || 'Unable to update staff', 'error') });
  if (!isRehabAdmin) return <div className="card p-6 text-sm text-secondary-500">Staff management is available to rehab administrators only.</div>;
  return <div className="space-y-5"><div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold text-secondary-800">Staff & access</h1><p className="text-sm text-secondary-500">Invite your team and tailor their access.</p></div><button className="btn-primary" onClick={() => setInviting(true)}><PlusIcon className="h-4 w-4" />Invite staff</button></div>
    {staff.isError && <ErrorBanner onRetry={() => staff.refetch()}>We could not load staff members. Please try again.</ErrorBanner>}
    {staff.isLoading ? <div className="card p-5"><SkeletonTable rows={5} cols={4} /></div> : staff.data?.length === 0 ? <EmptyState title="No staff members yet" description="Invite a colleague to help run this workspace." actionLabel="Invite staff" onAction={() => setInviting(true)} /> : <div className="table-wrap"><table><thead><tr><th>Team member</th><th>Roles</th><th>Extra access</th><th /></tr></thead><tbody>{staff.data?.map((member: any) => <tr key={member.id}><td><p className="font-medium text-secondary-800">{member.full_name || member.username}</p><p className="text-xs text-secondary-500">{member.email} · {member.tenant_user_id}</p></td><td>{member.roles?.map((role: any) => <span key={role.id} className="badge badge-draft mr-1">{role.name}</span>) || member.role}</td><td className="text-xs text-secondary-600">{member.extra_permissions?.length ? member.extra_permissions.join(', ') : '—'}</td><td><button className="rounded-lg p-2 text-primary-600 hover:bg-primary-50" title="Edit access" onClick={() => setEditing(member)}><PencilSquareIcon className="h-4 w-4" /></button></td></tr>)}</tbody></table></div>}
    {(inviting || editing) && <StaffModal member={editing} roles={roles.data || []} permissions={permissions.data || []} busy={create.isPending || update.isPending} onClose={() => { setInviting(false); setEditing(null); }} onSubmit={(body: any) => editing ? update.mutate({ id: editing.id, body }) : create.mutate(body)} />}
  </div>;
};

function StaffModal({ member, roles, permissions, busy, onClose, onSubmit }: any) {
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<InviteValues>({ resolver: zodResolver(inviteSchema), defaultValues: { email: member?.email || '', first_name: member?.first_name || '', last_name: member?.last_name || '', role: member?.roles?.[0]?.name || '', extra_permissions: member?.extra_permissions || [] } });
  const selectedRole = watch('role'); const extras = watch('extra_permissions') || []; const chosenRole = roles.find((role: any) => role.name === selectedRole);
  const toggle = (code: string) => setValue('extra_permissions', extras.includes(code) ? extras.filter((item: string) => item !== code) : [...extras, code]);
  const submit = (values: InviteValues) => onSubmit(values);
  return <div className="modal-overlay" onClick={onClose}><div className="modal-content max-h-[90vh] overflow-y-auto" onClick={(event) => event.stopPropagation()}><div className="mb-4 flex items-center justify-between"><div><h2 className="text-lg font-semibold text-secondary-800">{member ? 'Edit access' : 'Invite staff member'}</h2><p className="text-xs text-secondary-500">{member ? 'Role access is shown separately from individual grants.' : 'They will receive a single-use link to create their own password.'}</p></div><button onClick={onClose}><XMarkIcon className="h-5 w-5" /></button></div><form className="space-y-3" onSubmit={handleSubmit(submit)}><div className="grid grid-cols-2 gap-3"><Field label="First name"><input className="input-field" {...register('first_name')} /></Field><Field label="Last name"><input className="input-field" {...register('last_name')} /></Field></div><Field label="Email"><input className="input-field" type="email" {...register('email')} />{errors.email && <Error text="Enter a valid email" />}</Field><Field label="Role"><select className="input-field" {...register('role')}><option value="">Choose a role</option>{roles.map((role: any) => <option key={role.id} value={role.name}>{role.name}</option>)}</select></Field>{chosenRole && <div className="rounded-lg bg-primary-50 p-3 text-xs text-primary-800"><strong>Included with {chosenRole.name}:</strong> {chosenRole.permissions.join(', ') || 'No permissions'}</div>}{member && <fieldset><legend className="form-label">Extra individual permissions</legend><div className="grid max-h-44 grid-cols-1 gap-2 overflow-y-auto rounded-lg border border-slate-200 p-3">{permissions.map((permission: any) => <label key={permission.id} className="flex items-start gap-2 text-sm text-secondary-700"><input type="checkbox" checked={extras.includes(permission.codename)} onChange={() => toggle(permission.codename)} className="mt-0.5" /><span><span className="font-medium">{permission.name}</span><span className="ml-1 text-xs text-secondary-400">{permission.codename}</span></span></label>)}</div></fieldset>}<div className="flex gap-2 pt-2"><button className="btn-primary flex-1" disabled={busy}>{busy ? 'Saving…' : member ? 'Save changes' : 'Send invite'}</button><button type="button" className="btn-secondary flex-1" onClick={onClose}>Cancel</button></div></form></div></div>;
}
function Field({ label, children }: any) { return <label className="block"><span className="form-label">{label}</span>{children}</label>; }
function Error({ text }: { text: string }) { return <span className="text-xs text-danger">{text}</span>; }
export default Staff;
