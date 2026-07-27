import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from '@tanstack/react-router';
import api from '../api/client';
import PatientForm from '../components/PatientForm';

const fetchPatients = async () => {
  const { data } = await api.get('/patients/');
  return data;
};

const Patients: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const { data: patients, isLoading, error } = useQuery({
    queryKey: ['patients'],
    queryFn: fetchPatients,
  });

  if (isLoading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-500">Error loading patients</div>;

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Patients</h2>
        <button
          onClick={() => setShowForm(true)}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          + Add Patient
        </button>
      </div>
      {patients?.length === 0 ? (
        <p>No patients found. Add your first patient.</p>
      ) : (
        <ul className="space-y-2">
          {patients?.map((p: any) => (
            <li key={p.id} className="bg-white p-3 rounded shadow hover:bg-gray-50">
              <Link to={`/patients/${p.id}`} className="block">
                <span className="font-medium">{p.first_name} {p.last_name}</span> – {p.phone}
                <span className="ml-4 text-sm text-gray-500">Click to view details →</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
      {showForm && <PatientForm onClose={() => setShowForm(false)} />}
    </div>
  );
};

export default Patients;
