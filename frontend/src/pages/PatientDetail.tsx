import React, { useState } from 'react';
import { useParams, Link } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import api from '../api/client';
import PatientNotes from '../components/PatientNotes';
import PatientSponsors from '../components/PatientSponsors';

const fetchPatient = async (id: string) => {
  const { data } = await api.get(`/patients/${id}/`);
  return data;
};

const PatientDetail: React.FC = () => {
  const { id } = useParams({ from: '/patients/$id' });
  const [activeTab, setActiveTab] = useState<'info' | 'notes' | 'sponsors'>('info');
  const { data: patient, isLoading, error } = useQuery({
    queryKey: ['patient', id],
    queryFn: () => fetchPatient(id),
  });

  if (isLoading) return <div className="p-4">Loading patient...</div>;
  if (error) return <div className="p-4 text-red-500">Error loading patient</div>;

  return (
    <div className="p-4">
      <div className="mb-4">
        <Link to="/" className="text-blue-600 hover:underline">← Back to Patients</Link>
      </div>
      <h1 className="text-2xl font-bold mb-2">{patient.first_name} {patient.last_name}</h1>
      <p className="text-gray-600 mb-4">Phone: {patient.phone} | DOB: {patient.date_of_birth}</p>

      <div className="border-b mb-4">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('info')}
            className={`pb-2 px-2 ${activeTab === 'info' ? 'border-b-2 border-blue-600 font-medium' : 'text-gray-500'}`}
          >
            Info
          </button>
          <button
            onClick={() => setActiveTab('notes')}
            className={`pb-2 px-2 ${activeTab === 'notes' ? 'border-b-2 border-blue-600 font-medium' : 'text-gray-500'}`}
          >
            Clinical Notes
          </button>
          <button
            onClick={() => setActiveTab('sponsors')}
            className={`pb-2 px-2 ${activeTab === 'sponsors' ? 'border-b-2 border-blue-600 font-medium' : 'text-gray-500'}`}
          >
            Sponsors
          </button>
        </div>
      </div>

      {activeTab === 'info' && (
        <div className="bg-white p-4 rounded shadow">
          <p><strong>Gender:</strong> {patient.gender}</p>
          <p><strong>Email:</strong> {patient.email || 'N/A'}</p>
          <p><strong>Address:</strong> {patient.address || 'N/A'}</p>
          <p><strong>Emergency Contact:</strong> {patient.emergency_contact_name || 'N/A'} ({patient.emergency_contact_phone || 'N/A'})</p>
          <p><strong>Referring Doctor:</strong> {patient.referring_doctor || 'N/A'}</p>
          <p><strong>Status:</strong> {patient.status}</p>
          <p><strong>Intake Date:</strong> {new Date(patient.intake_date).toLocaleDateString()}</p>
        </div>
      )}

      {activeTab === 'notes' && <PatientNotes patientId={Number(id)} />}
      {activeTab === 'sponsors' && <PatientSponsors patientId={Number(id)} />}
    </div>
  );
};

export default PatientDetail;
