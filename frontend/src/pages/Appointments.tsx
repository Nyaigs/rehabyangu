import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/client';
import AppointmentForm from '../components/AppointmentForm';

const fetchAppointments = async () => {
  const { data } = await api.get('/appointments/');
  return data;
};

const Appointments: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const { data: appointments, isLoading, error } = useQuery({
    queryKey: ['appointments'],
    queryFn: fetchAppointments,
  });

  if (isLoading) return <div className="p-4">Loading appointments...</div>;
  if (error) return <div className="p-4 text-red-500">Error loading appointments</div>;

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Appointments</h2>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          + Book Appointment
        </button>
      </div>
      {appointments?.length === 0 ? (
        <p>No appointments scheduled. Book your first appointment.</p>
      ) : (
        <ul className="space-y-2">
          {appointments?.map((a: any) => (
            <li key={a.id} className="bg-white p-3 rounded shadow flex justify-between items-center">
              <div>
                <span className="font-medium">{a.patient_name || a.patient}</span>
                <span className="ml-2 text-sm text-gray-500">with {a.clinician_name || a.clinician}</span>
                <span className="ml-2 text-sm text-gray-600">
                  {new Date(a.start_time).toLocaleString()}
                </span>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                a.status === 'completed' ? 'bg-green-100 text-green-800' :
                a.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                a.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                'bg-blue-100 text-blue-800'
              }`}>
                {a.status || 'scheduled'}
              </span>
            </li>
          ))}
        </ul>
      )}
      {showForm && <AppointmentForm onClose={() => setShowForm(false)} />}
    </div>
  );
};

export default Appointments;
