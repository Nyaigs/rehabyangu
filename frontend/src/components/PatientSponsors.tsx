import React, { useState } from 'react';
import { usePatientSponsors } from '../hooks/usePatientSponsors';
import SponsorForm from './SponsorForm';

interface Props {
  patientId: number;
}

const PatientSponsors: React.FC<Props> = ({ patientId }) => {
  const [showForm, setShowForm] = useState(false);
  const { data: sponsors, isLoading, error } = usePatientSponsors(patientId);

  if (isLoading) return <div>Loading sponsors...</div>;
  if (error) return <div className="text-red-500">Error loading sponsors</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Sponsors</h3>
        <button onClick={() => setShowForm(true)} className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
          + Add Sponsor
        </button>
      </div>
      {sponsors?.length === 0 ? (
        <p className="text-gray-500">No sponsors linked yet.</p>
      ) : (
        <div className="space-y-2">
          {sponsors?.map((s: any) => (
            <div key={s.id} className="bg-gray-50 p-3 rounded border flex justify-between items-center">
              <div>
                <span className="font-medium">{s.full_name}</span>
                <span className="ml-2 text-sm text-gray-500">{s.relationship}</span>
                {s.company_name && <span className="ml-2 text-sm text-gray-500">({s.company_name})</span>}
                <div className="text-sm text-gray-600">{s.phone}</div>
              </div>
              {s.email && <div className="text-sm text-gray-500">{s.email}</div>}
            </div>
          ))}
        </div>
      )}
      {showForm && <SponsorForm patientId={patientId} onClose={() => setShowForm(false)} />}
    </div>
  );
};

export default PatientSponsors;
