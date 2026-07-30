import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PlusIcon, CalendarDaysIcon, UserIcon, ClockIcon } from '@heroicons/react/24/outline';
import api from '../api/client';
import { SkeletonTable, SkeletonText } from '../components/Skeleton';
import { EmptyState } from '../components/EmptyState';
import { useToast } from '../context/ToastContext';

const fetchAppointments = async () => {
  const { data } = await api.get('/appointments/');
  return data;
};

const fetchPatients = async () => {
  const { data } = await api.get('/patients/');
  return data;
};

const createAppointment = async (payload: any) => {
  const { data } = await api.post('/appointments/', payload);
  return data;
};

const Appointments: React.FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    patient: '',
    clinician: '',
    start_time: '',
    end_time: '',
    notes: '',
  });
  const [error, setError] = useState('');

  const { data: appointments, isLoading: appointmentsLoading } = useQuery({
    queryKey: ['appointments'],
    queryFn: fetchAppointments,
  });

  const { data: patients } = useQuery({
    queryKey: ['patients'],
    queryFn: fetchPatients,
  });

  const mutation = useMutation({
    mutationFn: createAppointment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['appointments'] });
      setShowForm(false);
      setFormData({ patient: '', clinician: '', start_time: '', end_time: '', notes: '' });
      toast.showToast('Appointment booked successfully', 'success');
    },
    onError: (error: any) => {
      setError(error.response?.data?.error || 'Failed to book appointment');
      toast.showToast('Failed to book appointment', 'error');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    mutation.mutate(formData);
  };

  if (appointmentsLoading) {
    return (
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <SkeletonText width="w-32" className="mb-1" />
            <SkeletonText width="w-48" />
          </div>
          <SkeletonText width="w-32" className="h-8" />
        </div>
        <SkeletonTable rows={5} cols={4} />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <h1 className="text-2xl font-bold text-secondary-800">Appointments</h1>
          <p className="text-sm text-secondary-500">Manage all patient appointments</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary">
          <PlusIcon className="w-4 h-4" />
          Book Appointment
        </button>
      </div>

      {appointments?.length === 0 ? (
        <EmptyState
          title="No appointments"
          description="Book your first appointment."
          actionLabel="Book Appointment"
          onAction={() => setShowForm(true)}
          iconType="inbox"
        />
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Patient</th>
                <th>Clinician</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {appointments?.map((a: any) => (
                <tr key={a.id}>
                  <td className="font-medium text-secondary-800">
                    {a.patient_name || `Patient #${a.patient}`}
                  </td>
                  <td>{a.clinician_name || a.clinician}</td>
                  <td>{new Date(a.start_time).toLocaleString()}</td>
                  <td>{new Date(a.end_time).toLocaleString()}</td>
                  <td>
                    <span className={`badge ${
                      a.status === 'completed' ? 'badge-paid' :
                      a.status === 'cancelled' ? 'badge-suspended' :
                      a.status === 'in_progress' ? 'badge-warning' :
                      'badge-trial'
                    }`}>
                      {a.status || 'scheduled'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal-content animate-scaleIn" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-secondary-800">Book Appointment</h2>
              <button onClick={() => setShowForm(false)} className="text-secondary-400 hover:text-secondary-600">
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="space-y-3">
                <div>
                  <label className="form-label">Patient *</label>
                  <select
                    className="input-field"
                    value={formData.patient}
                    onChange={(e) => setFormData({ ...formData, patient: e.target.value })}
                    required
                  >
                    <option value="">Select patient</option>
                    {patients?.map((p: any) => (
                      <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="form-label">Clinician</label>
                  <input
                    type="text"
                    className="input-field"
                    value={formData.clinician}
                    onChange={(e) => setFormData({ ...formData, clinician: e.target.value })}
                    placeholder="Clinician name"
                  />
                </div>
                <div>
                  <label className="form-label">Start Time *</label>
                  <input
                    type="datetime-local"
                    className="input-field"
                    value={formData.start_time}
                    onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label">End Time *</label>
                  <input
                    type="datetime-local"
                    className="input-field"
                    value={formData.end_time}
                    onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="form-label">Notes</label>
                  <textarea
                    className="input-field"
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    rows={2}
                    placeholder="Additional notes..."
                  />
                </div>
                {error && <p className="text-danger text-sm">{error}</p>}
                <button type="submit" disabled={mutation.isPending} className="btn-primary w-full justify-center">
                  {mutation.isPending ? 'Booking...' : 'Book Appointment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Appointments;
