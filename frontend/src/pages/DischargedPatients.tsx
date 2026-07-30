import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { CheckIcon, XMarkIcon, UserGroupIcon } from '@heroicons/react/24/outline';
import api from '../api/client';

const fetchDischarged = async () => {
  const { data } = await api.get('/discharged-patients/');
  return data;
};

const DischargedPatients: React.FC = () => {
  const { data, isLoading } = useQuery({ queryKey: ['discharged-patients'], queryFn: fetchDischarged });

  if (isLoading) return <div className="p-4">Loading...</div>;

  return (
    <div className="p-4">
      <div className="flex items-center gap-2 mb-4">
        <UserGroupIcon className="w-5 h-5 text-gray-700" />
        <h2 className="text-xl font-bold">Discharged Patients</h2>
      </div>
      {data?.length === 0 ? (
        <p className="text-gray-500">No discharged patients.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border rounded">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-2 border text-left text-sm font-medium text-gray-700">Name</th>
                <th className="px-4 py-2 border text-left text-sm font-medium text-gray-700">Discharged At</th>
                <th className="px-4 py-2 border text-left text-sm font-medium text-gray-700">Balance</th>
                <th className="px-4 py-2 border text-left text-sm font-medium text-gray-700">Force</th>
                <th className="px-4 py-2 border text-left text-sm font-medium text-gray-700">Reason</th>
                <th className="px-4 py-2 border text-left text-sm font-medium text-gray-700">Approved By</th>
              </tr>
            </thead>
            <tbody>
              {data?.map((p: any) => (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2 border text-sm">{p.first_name} {p.last_name}</td>
                  <td className="px-4 py-2 border text-sm">{new Date(p.discharged_at).toLocaleDateString()}</td>
                  <td className={`px-4 py-2 border text-sm font-medium ${p.balance > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    KES {p.balance}
                  </td>
                  <td className="px-4 py-2 border text-sm text-center">
                    {p.is_force ? (
                      <CheckIcon className="w-4 h-4 text-green-600 mx-auto" />
                    ) : (
                      <XMarkIcon className="w-4 h-4 text-gray-400 mx-auto" />
                    )}
                  </td>
                  <td className="px-4 py-2 border text-sm max-w-xs truncate">{p.discharge_reason || 'N/A'}</td>
                  <td className="px-4 py-2 border text-sm">{p.approved_by || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default DischargedPatients;