import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { PhoneIcon, EnvelopeIcon } from '@heroicons/react/24/outline';
import api from '../api/client';
import { SkeletonTable, SkeletonText } from '../components/Skeleton';
import { EmptyState } from '../components/EmptyState';

const fetchSponsors = async () => {
  const { data } = await api.get('/sponsors/');
  return data;
};

const Sponsors: React.FC = () => {
  const { data: sponsors, isLoading } = useQuery({
    queryKey: ['sponsors'],
    queryFn: fetchSponsors,
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div>
          <SkeletonText width="w-32" className="mb-1" />
          <SkeletonText width="w-48" />
        </div>
        <SkeletonTable rows={5} cols={4} />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-secondary-800">Sponsors</h1>
        <p className="text-sm text-secondary-500">Manage all sponsors linked to patients</p>
      </div>

      {sponsors?.length === 0 ? (
        <EmptyState
          title="No sponsors found"
          description="Link sponsors to patients to track who pays for their care."
          iconType="users"
        />
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Sponsor Name</th>
                <th>Patient</th>
                <th>Relationship</th>
                <th>Contact</th>
              </tr>
            </thead>
            <tbody>
              {sponsors?.map((s: any) => (
                <tr key={s.id}>
                  <td className="font-medium text-secondary-800">{s.full_name}</td>
                  <td>{s.patient_name || `Patient #${s.patient}`}</td>
                  <td><span className="badge badge-draft">{s.relationship}</span></td>
                  <td>
                    <div className="flex flex-col text-sm">
                      <span className="flex items-center gap-1"><PhoneIcon className="w-3.5 h-3.5" />{s.phone}</span>
                      {s.email && <span className="flex items-center gap-1"><EnvelopeIcon className="w-3.5 h-3.5" />{s.email}</span>}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Sponsors;
