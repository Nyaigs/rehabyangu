import { useMemo, useState } from 'react';
import { Link } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowDownTrayIcon,
  MagnifyingGlassIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';
import api from '../../api/client';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/Button';
import { ErrorBanner } from '../../components/ErrorBanner';
import { EmptyState } from '../../components/EmptyState';

interface AuditEntry {
  id: number;
  actor: number | null;
  actor_username: string | null;
  actor_tenant_user_id: string | null;
  tenant: number;
  action: string;
  description: string;
  ip_address: string | null;
  timestamp: string;
}

const ACTION_TONES: Record<string, string> = {
  LOGIN: 'bg-blue-50 text-blue-700',
  LOGOUT: 'bg-slate-100 text-slate-700',
  CREATE: 'bg-emerald-50 text-emerald-700',
  UPDATE: 'bg-amber-50 text-amber-700',
  DELETE: 'bg-rose-50 text-rose-700',
  READ: 'bg-sky-50 text-sky-700',
  SUSPEND: 'bg-rose-50 text-rose-700',
  REACTIVATE: 'bg-emerald-50 text-emerald-700',
};

function formatTimestamp(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

export default function AuditLogPage() {
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [daysFilter, setDaysFilter] = useState(7);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: async () => (await api.get('/audit-logs/')).data,
    refetchInterval: 30000,
  });

  const entries: AuditEntry[] = Array.isArray(data) ? data : data?.results ?? [];

  const filtered = useMemo(() => {
    const cutoff = Date.now() - daysFilter * 24 * 60 * 60 * 1000;
    const q = search.trim().toLowerCase();
    return entries.filter((e) => {
      if (new Date(e.timestamp).getTime() < cutoff) return false;
      if (actionFilter && e.action !== actionFilter) return false;
      if (q) {
        const haystack = `${e.actor_username ?? ''} ${e.description} ${e.ip_address ?? ''}`.toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }, [entries, search, actionFilter, daysFilter]);

  const actionOptions = useMemo(() => {
    const set = new Set(entries.map((e) => e.action));
    return Array.from(set).sort();
  }, [entries]);

  const exportCsv = () => {
    const header = ['Timestamp', 'Actor', 'Action', 'Description', 'IP Address'];
    const rows = filtered.map((e) => [
      e.timestamp,
      e.actor_username ?? '',
      e.action,
      e.description.replace(/"/g, '""'),
      e.ip_address ?? '',
    ]);
    const csv = [header, ...rows]
      .map((r) => r.map((cell) => `"${cell}"`).join(','))
      .join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-log-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="mb-1 text-sm font-medium text-[#237a67]">Compliance</p>
          <h1 className="text-2xl font-bold text-slate-900">Audit log</h1>
          <p className="mt-1 text-sm text-slate-500">
            Every action in your facility, with second-level timestamps. Immutable and tamper-proof.
          </p>
        </div>
      </div>

      <nav className="flex gap-2 border-b border-slate-100 pb-3">
        <Link to="/settings" className="rounded-lg px-3 py-1.5 text-sm font-semibold text-slate-600 hover:bg-slate-50">Facility settings</Link>
        <Link to="/settings/subscription" className="rounded-lg px-3 py-1.5 text-sm font-semibold text-slate-600 hover:bg-slate-50">Subscription</Link>
        <span className="rounded-lg bg-[#17614f] px-3 py-1.5 text-sm font-semibold text-white">Audit log</span>
      </nav>

      <div className="hidden">
        <Button
          variant="secondary"
          onClick={exportCsv}
          className="w-auto border-slate-200 bg-white"
          disabled={!filtered.length}
        >
          <ArrowDownTrayIcon className="mr-1.5 h-4 w-4" />
          Export CSV
        </Button>
      </div>

      <Card className="border-slate-200/80 bg-white shadow-[0_2px_8px_rgba(15,46,61,0.04)]">
        <CardContent className="p-4 sm:p-5">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-4">
            <label className="relative block sm:col-span-2">
              <span className="sr-only">Search audit log</span>
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by user, description, or IP"
                className="h-10 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-[#17614f] focus:outline-none focus:ring-2 focus:ring-emerald-100"
              />
            </label>
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700 focus:border-[#17614f] focus:outline-none"
            >
              <option value="">All actions</option>
              {actionOptions.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
            <select
              value={daysFilter}
              onChange={(e) => setDaysFilter(Number(e.target.value))}
              className="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700 focus:border-[#17614f] focus:outline-none"
            >
              <option value={1}>Last 24 hours</option>
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {isError && (
        <ErrorBanner onRetry={() => refetch()}>
          We could not load the audit log. Please try again.
        </ErrorBanner>
      )}

      <Card className="border-slate-200/80 bg-white shadow-[0_2px_8px_rgba(15,46,61,0.04)]">
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-3 p-5">
              {[0, 1, 2, 3, 4].map((i) => (
                <div key={i} className="h-10 animate-pulse rounded bg-slate-100" />
              ))}
            </div>
          ) : !filtered.length ? (
            <div className="p-10">
              <EmptyState
                title="No audit events match your filters"
                description="Try widening the date range or clearing the search."
                iconType="inbox"
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-100 bg-slate-50/50">
                  <tr className="text-xs uppercase tracking-wide text-slate-500">
                    <th className="px-4 py-3 font-semibold">Timestamp</th>
                    <th className="px-4 py-3 font-semibold">User</th>
                    <th className="px-4 py-3 font-semibold">Action</th>
                    <th className="px-4 py-3 font-semibold">Description</th>
                    <th className="px-4 py-3 font-semibold">IP</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filtered.slice(0, 200).map((entry) => (
                    <tr key={entry.id} className="hover:bg-slate-50">
                      <td className="whitespace-nowrap px-4 py-3 font-mono text-xs text-slate-600">
                        {formatTimestamp(entry.timestamp)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-medium text-slate-800">
                          {entry.actor_username ?? '—'}
                        </div>
                        {entry.actor_tenant_user_id && (
                          <div className="font-mono text-xs text-slate-500">
                            {entry.actor_tenant_user_id}
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${
                            ACTION_TONES[entry.action] ?? 'bg-slate-100 text-slate-700'
                          }`}
                        >
                          {entry.action}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-700">{entry.description}</td>
                      <td className="whitespace-nowrap px-4 py-3 font-mono text-xs text-slate-500">
                        {entry.ip_address ?? '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filtered.length > 200 && (
                <p className="border-t border-slate-100 px-4 py-3 text-xs text-slate-500">
                  Showing the 200 most recent matching events. Refine the filters to narrow down.
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <p className="flex items-center gap-2 text-xs text-slate-500">
        <ShieldCheckIcon className="h-4 w-4 text-[#237a67]" />
        Audit records are immutable. Updates and deletions are blocked at the database level.
      </p>
    </div>
  );
}
