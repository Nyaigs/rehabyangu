import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ExclamationTriangleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import api from '../api/client';

const fetchPending = async () => {
  const { data } = await api.get('/discharge-requests/pending/');
  return data;
};

const approveRequest = async ({ id, password, approval_reason }: any) => {
  const { data } = await api.post(`/discharge-requests/${id}/approve/`, { password, approval_reason });
  return data;
};

const rejectRequest = async ({ id, rejection_reason }: any) => {
  const { data } = await api.post(`/discharge-requests/${id}/reject/`, { rejection_reason });
  return data;
};

const PendingDischarges: React.FC = () => {
  const queryClient = useQueryClient();
  const { data, isLoading, refetch } = useQuery({ queryKey: ['pending-discharges'], queryFn: fetchPending });

  const approveMutation = useMutation({
    mutationFn: approveRequest,
    onSuccess: () => {
      refetch();
      alert('Discharge approved!');
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'Approval failed');
    }
  });

  const rejectMutation = useMutation({
    mutationFn: rejectRequest,
    onSuccess: () => {
      refetch();
      alert('Discharge rejected.');
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'Rejection failed');
    }
  });

  const handleApprove = (id: number) => {
    const password = prompt('Enter your admin password:');
    if (!password) return;
    const reason = prompt('Approval reason (optional):') || '';
    approveMutation.mutate({ id, password, approval_reason: reason });
  };

  const handleReject = (id: number) => {
    const reason = prompt('Rejection reason:');
    if (reason) rejectMutation.mutate({ id, rejection_reason: reason });
  };

  if (isLoading) return <div className="p-4">Loading...</div>;

  return (
    <div className="p-4">
      <div className="flex items-center gap-2 mb-4">
        <ClockIcon className="w-5 h-5 text-yellow-600" />
        <h2 className="text-xl font-bold">Pending Discharge Approvals</h2>
      </div>
      {data?.length === 0 ? (
        <p className="text-gray-500">No pending discharge requests.</p>
      ) : (
        <div className="space-y-4">
          {data?.map((req: any) => (
            <div key={req.id} className="bg-white p-4 rounded shadow border-l-4 border-yellow-400">
              <div className="flex flex-col md:flex-row justify-between items-start gap-4">
                <div className="flex-1">
                  <p className="font-semibold text-lg">{req.patient_name}</p>
                  <p className="text-sm text-gray-600">
                    Requested by: <span className="font-medium">{req.requested_by}</span>
                  </p>
                  <p className="text-sm text-gray-600">Reason: {req.reason}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(req.requested_at).toLocaleString()}
                  </p>
                  {req.is_force && (
                    <span className="inline-flex items-center gap-1 mt-1 text-red-600 text-sm font-semibold bg-red-50 px-2 py-0.5 rounded">
                      <ExclamationTriangleIcon className="w-4 h-4" />
                      Force discharge
                    </span>
                  )}
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <button
                    onClick={() => handleApprove(req.id)}
                    className="inline-flex items-center gap-1 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-sm"
                  >
                    <CheckCircleIcon className="w-4 h-4" />
                    Approve
                  </button>
                  <button
                    onClick={() => handleReject(req.id)}
                    className="inline-flex items-center gap-1 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 text-sm"
                  >
                    <XCircleIcon className="w-4 h-4" />
                    Reject
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PendingDischarges;