import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/client';
import { SkeletonText, SkeletonCard } from '../components/Skeleton';
import { EmptyState } from '../components/EmptyState';
import VitalsComponent from '../components/VitalsComponent';

const Vitals: React.FC = () => {
  const [selectedPatient, setSelectedPatient] = useState<number | null>(null);
  const { data: patients, isLoading: patientsLoading } = useQuery({
    queryKey: ['patients'],
    queryFn: async () => {
      const { data } = await api.get('/patients/');
      return data;
    },
  });

  if (patientsLoading) {
    return (
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <SkeletonText width="w-32" className="mb-1" />
            <SkeletonText width="w-48" />
          </div>
        </div>
        <SkeletonCard count={1} />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-secondary-800">Vitals Management</h1>
        <p className="text-sm text-secondary-500">Record and track patient vital signs</p>
      </div>

      <div className="card p-4">
        <label className="form-label">Select Patient</label>
        <select
          className="input-field max-w-md"
          value={selectedPatient || ''}
          onChange={(e) => setSelectedPatient(Number(e.target.value))}
        >
          <option value="">Select a patient</option>
          {patients?.map((p: any) => (
            <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
          ))}
        </select>
      </div>

      {selectedPatient ? (
        <VitalsComponent patientId={selectedPatient} />
      ) : (
        <EmptyState
          title="Select a patient"
          description="Choose a patient to view and record their vitals."
          iconType="users"
        />
      )}
    </div>
  );
};

export default Vitals;
