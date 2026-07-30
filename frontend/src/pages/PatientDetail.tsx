import React, { useState } from 'react';
import { useParams, Link, useNavigate } from '@tanstack/react-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ExclamationTriangleIcon,
  ArrowLeftIcon,
  UserIcon,
  PhoneIcon,
  CalendarIcon,
  DocumentTextIcon,
  HeartIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';
import api from '../api/client';
import PatientNotes from '../components/PatientNotes';
import PatientSponsors from '../components/PatientSponsors';
import VitalsComponent from '../components/VitalsComponent';
import { useToast } from '../context/ToastContext';
import { SkeletonText, SkeletonCard } from '../components/Skeleton';

const fetchPatient = async (id: string) => {
  const { data } = await api.get(`/patients/${id}/`);
  return data;
};

const fetchPatientBill = async (id: number) => {
  const { data } = await api.get(`/patient-bill/${id}/`);
  return data;
};

const PatientDetail: React.FC = () => {
  const { id } = useParams({ from: '/patients/$id' });
  const navigate = useNavigate();
  const toast = useToast();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<'info' | 'notes' | 'vitals' | 'sponsors'>('info');
  const [showDischargeModal, setShowDischargeModal] = useState(false);
  const [forceDischarge, setForceDischarge] = useState(false);
  const [reason, setReason] = useState('');
  const [dischargeError, setDischargeError] = useState('');

  const { data: patient, isLoading, error } = useQuery({
    queryKey: ['patient', id],
    queryFn: () => fetchPatient(id),
  });

  const { data: bill } = useQuery({
    queryKey: ['patient-bill', id],
    queryFn: () => fetchPatientBill(Number(id)),
    enabled: !!id,
  });

  const requestDischargeMutation = useMutation({
    mutationFn: async () => {
      const payload: any = { reason: reason, force: forceDischarge };
      const response = await api.post(`/patients/${id}/request-discharge/`, payload);
      return response.data;
    },
    onSuccess: () => {
      toast.showToast('Discharge request submitted. Awaiting director approval.', 'success');
      setShowDischargeModal(false);
      queryClient.invalidateQueries({ queryKey: ['patient', id] });
    },
    onError: (error: any) => {
      const errMsg = error.response?.data?.error || 'Failed to submit request';
      setDischargeError(errMsg);
      toast.showToast(errMsg, 'error');
    },
  });

  const handleDischargeClick = () => {
    setDischargeError('');
    setForceDischarge(false);
    setReason('');
    setShowDischargeModal(true);
  };

  const handleDischargeConfirm = () => {
    if (forceDischarge && !reason.trim()) {
      setDischargeError('Reason is required for force discharge');
      return;
    }
    requestDischargeMutation.mutate();
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <SkeletonText width="w-24" />
          <SkeletonText width="w-32" />
        </div>
        <SkeletonCard count={1} />
      </div>
    );
  }
  if (error) return <div className="text-danger text-sm p-4">Error loading patient.</div>;
  if (!patient) return <div className="text-secondary-500 p-4">Patient not found.</div>;

  const balance = bill ? parseFloat(bill.total_balance) : 0;
  const isDischarged = patient.status === 'discharged';

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <Link to="/patients" className="inline-flex items-center gap-1 text-primary-600 hover:text-primary-700 text-sm font-medium">
          <ArrowLeftIcon className="w-4 h-4" /> Back to Patients
        </Link>
        <button onClick={handleDischargeClick} disabled={isDischarged || requestDischargeMutation.isPending} className={`btn-danger text-sm ${isDischarged ? 'opacity-50 cursor-not-allowed' : ''}`}>
          {requestDischargeMutation.isPending ? 'Submitting...' : isDischarged ? 'Discharged' : 'Request Discharge'}
        </button>
      </div>

      <div className="card p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-secondary-800">{patient.first_name} {patient.last_name}</h1>
          <div className="flex flex-wrap items-center gap-3 text-sm text-secondary-500 mt-1">
            <span className="flex items-center gap-1"><PhoneIcon className="w-3.5 h-3.5" />{patient.phone}</span>
            <span className="flex items-center gap-1"><CalendarIcon className="w-3.5 h-3.5" />{new Date(patient.date_of_birth).toLocaleDateString()}</span>
            {isDischarged && <span className="badge badge-suspended">Discharged on {new Date(patient.discharged_at).toLocaleDateString()}</span>}
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-secondary-500">Current Balance</div>
          <div className={`text-xl font-bold ${balance > 0 ? 'text-danger' : 'text-accent'}`}>
            KES {balance.toFixed(2)}
            {balance > 0 && !isDischarged && <span className="text-sm ml-2 text-danger">(Outstanding)</span>}
          </div>
        </div>
      </div>

      <div className="border-b border-secondary-200">
        <div className="flex flex-wrap gap-2">
          {[
            { key: 'info', label: 'Info', icon: UserIcon },
            { key: 'notes', label: 'Clinical Notes', icon: DocumentTextIcon },
            { key: 'vitals', label: 'Vitals', icon: HeartIcon },
            { key: 'sponsors', label: 'Sponsors', icon: UserGroupIcon },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`pb-2 px-3 text-sm font-medium flex items-center gap-1.5 transition-colors ${
                activeTab === tab.key ? 'border-b-2 border-primary-600 text-primary-700' : 'text-secondary-500 hover:text-secondary-700'
              }`}
            >
              <tab.icon className="w-4 h-4" /> {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="py-2">
        {activeTab === 'info' && (
          <div className="card p-4 space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
              <div><span className="font-medium text-secondary-600">Gender:</span> {patient.gender}</div>
              <div><span className="font-medium text-secondary-600">Email:</span> {patient.email || 'N/A'}</div>
              <div><span className="font-medium text-secondary-600">Address:</span> {patient.address || 'N/A'}</div>
              <div><span className="font-medium text-secondary-600">Emergency Contact:</span> {patient.emergency_contact_name || 'N/A'} ({patient.emergency_contact_phone || 'N/A'})</div>
              <div><span className="font-medium text-secondary-600">Referring Doctor:</span> {patient.referring_doctor || 'N/A'}</div>
              <div><span className="font-medium text-secondary-600">Status:</span> <span className="capitalize">{patient.status}</span></div>
              <div><span className="font-medium text-secondary-600">Intake Date:</span> {new Date(patient.intake_date).toLocaleDateString()}</div>
            </div>
            {patient.notes && (
              <div className="mt-2 p-3 bg-secondary-50 rounded-lg text-sm">
                <span className="font-medium text-secondary-600">Notes:</span>
                <pre className="whitespace-pre-wrap text-secondary-700 mt-1">{patient.notes}</pre>
              </div>
            )}
          </div>
        )}
        {activeTab === 'notes' && <PatientNotes patientId={Number(id)} />}
        {activeTab === 'vitals' && <VitalsComponent patientId={Number(id)} />}
        {activeTab === 'sponsors' && <PatientSponsors patientId={Number(id)} />}
      </div>

      {showDischargeModal && (
        <div className="modal-overlay" onClick={() => setShowDischargeModal(false)}>
          <div className="modal-content animate-scaleIn" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-semibold text-secondary-800 mb-2">Request Discharge</h2>
            <p className="text-sm text-secondary-500 mb-4">
              Submit a discharge request for <span className="font-medium">{patient.first_name} {patient.last_name}</span>.
              {!forceDischarge && <span className="block mt-1 text-xs">This will be sent for approval.</span>}
            </p>

            {balance > 0 && (
              <div className="bg-danger-light border border-danger/20 p-3 rounded-lg mb-4 flex items-start gap-2 text-sm text-danger">
                <ExclamationTriangleIcon className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <div>
                  <span className="font-medium">Outstanding Balance: KES {balance.toFixed(2)}</span>
                  <p className="text-xs">Normal discharge requires balance to be cleared. You may request a force discharge.</p>
                </div>
              </div>
            )}

            {balance > 0 && (
              <div className="space-y-3 mb-4">
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={forceDischarge} onChange={(e) => setForceDischarge(e.target.checked)} className="accent-primary-600" />
                  Request Force Discharge (Override)
                </label>
                {forceDischarge && (
                  <div>
                    <label className="form-label">Reason for force discharge *</label>
                    <textarea className="input-field" value={reason} onChange={(e) => setReason(e.target.value)} rows={3} placeholder="Explain why this patient is being discharged with outstanding balance..." />
                  </div>
                )}
                {dischargeError && (
                  <div className="text-sm text-danger flex items-center gap-1">
                    <ExclamationTriangleIcon className="w-4 h-4" /> {dischargeError}
                  </div>
                )}
              </div>
            )}

            {balance === 0 && (
              <div className="mb-4">
                <label className="form-label">Reason for discharge (optional)</label>
                <textarea className="input-field" value={reason} onChange={(e) => setReason(e.target.value)} rows={2} placeholder="Optional reason..." />
              </div>
            )}

            <div className="flex gap-2">
              <button onClick={handleDischargeConfirm} disabled={requestDischargeMutation.isPending} className="btn-primary flex-1 justify-center">
                {requestDischargeMutation.isPending ? 'Submitting...' : 'Submit Request'}
              </button>
              <button onClick={() => { setShowDischargeModal(false); setForceDischarge(false); setReason(''); setDischargeError(''); }} className="btn-secondary flex-1 justify-center">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientDetail;
