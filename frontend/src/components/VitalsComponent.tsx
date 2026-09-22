import { useQuery } from '@tanstack/react-query';
import api from '../api/client';
import { Badge } from './ui/Badge';
import { Table } from './ui/Table';
import { EmptyState } from './EmptyState';
import { ErrorBanner } from './ErrorBanner';
import { SkeletonTable } from './Skeleton';

const abnormal = (v: any) => v.abnormality_level && v.abnormality_level !== 'normal';
export default function VitalsComponent({ patientId }: { patientId: number }) {
  const vitals = useQuery({ queryKey: ['vitals', patientId], queryFn: async () => (await api.get('/vitals/', { params: { patient: patientId } })).data });
  if (vitals.isLoading) return <SkeletonTable rows={4} cols={6} />;
  if (vitals.isError) return <ErrorBanner>We could not load vital signs. Try again shortly.</ErrorBanner>;
  if (!vitals.data?.length) return <EmptyState title="No vitals recorded" description="Record observations from the Vitals workspace." iconType="inbox" />;
  return <div className="space-y-3"><div><h2 className="text-section-title text-secondary-800">Vitals history</h2><p className="text-body text-secondary-500">Abnormal observations are highlighted for follow-up.</p></div><Table><thead><tr><th>Recorded</th><th>Temperature</th><th>Blood pressure</th><th>Heart rate</th><th>Respiratory</th><th>Oxygen</th><th>Alert</th></tr></thead><tbody>{vitals.data.map((v: any) => <tr className={abnormal(v) ? 'bg-amber-50/50' : ''} key={v.id}><td>{new Date(v.date_measured || v.recorded_at).toLocaleString()}</td><td>{v.temperature ? `${v.temperature} °C` : '—'}</td><td>{v.systolic_bp ? `${v.systolic_bp}/${v.diastolic_bp}` : '—'}</td><td>{v.heart_rate || '—'}</td><td>{v.respiratory_rate || '—'}</td><td>{v.oxygen_saturation ? `${v.oxygen_saturation}%` : '—'}</td><td>{abnormal(v) && <Badge tone={v.abnormality_level === 'critical' ? 'danger' : 'warning'}>{v.abnormality_level}</Badge>}</td></tr>)}</tbody></Table></div>;
}
