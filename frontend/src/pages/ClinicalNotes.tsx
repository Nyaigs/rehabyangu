import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { PlusIcon, UserIcon } from '@heroicons/react/24/outline';
import api from '../api/client';
import { SkeletonCard, SkeletonText } from '../components/Skeleton';
import { EmptyState } from '../components/EmptyState';
import AddNoteModal from '../components/AddNoteModal';

const fetchClinicalNotes = async () => {
  const { data } = await api.get('/clinical-notes/');
  return data;
};

const fetchPatients = async () => {
  const { data } = await api.get('/patients/');
  return data;
};

const ClinicalNotes: React.FC = () => {
  const [selectedPatient, setSelectedPatient] = useState<number | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);

  const { data: notes, isLoading: notesLoading } = useQuery({
    queryKey: ['clinical-notes', selectedPatient],
    queryFn: fetchClinicalNotes,
  });

  const { data: patients } = useQuery({
    queryKey: ['patients'],
    queryFn: fetchPatients,
  });

  const filteredNotes = selectedPatient
    ? notes?.filter((n: any) => n.patient === selectedPatient)
    : notes;

  if (notesLoading) {
    return (
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <SkeletonText width="w-32" className="mb-1" />
            <SkeletonText width="w-48" />
          </div>
          <SkeletonText width="w-32" className="h-8" />
        </div>
        <SkeletonCard count={3} />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <h1 className="text-2xl font-bold text-secondary-800">Clinical Notes</h1>
          <p className="text-sm text-secondary-500">View and manage all SOAP notes</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="btn-primary">
          <PlusIcon className="w-4 h-4" />
          Add Note
        </button>
      </div>

      {/* Filter by patient */}
      <div className="card p-3 flex items-center gap-2">
        <UserIcon className="w-4 h-4 text-secondary-400" />
        <select
          className="input-field border-none p-0 text-sm focus:ring-0 max-w-xs"
          value={selectedPatient || ''}
          onChange={(e) => setSelectedPatient(e.target.value ? Number(e.target.value) : null)}
        >
          <option value="">All Patients</option>
          {patients?.map((p: any) => (
            <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
          ))}
        </select>
      </div>

      {!filteredNotes || filteredNotes.length === 0 ? (
        <EmptyState
          title="No clinical notes yet"
          description="Start documenting patient care by adding your first SOAP note."
          actionLabel="Add Note"
          onAction={() => setShowAddModal(true)}
          iconType="documents"
        />
      ) : (
        <div className="space-y-4">
          {filteredNotes.map((note: any) => (
            <div key={note.id} className="card p-4 hover:shadow-card-hover transition-shadow">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-secondary-800">
                      {note.patient_name || `Patient #${note.patient}`}
                    </span>
                    <span className="badge badge-draft text-[10px]">SOAP</span>
                    <span className="text-xs text-secondary-400">
                      {new Date(note.date).toLocaleString()}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 mt-2 text-sm">
                    <div>
                      <span className="font-medium text-secondary-600">S:</span>
                      <span className="text-secondary-700 ml-1">{note.subjective}</span>
                    </div>
                    <div>
                      <span className="font-medium text-secondary-600">O:</span>
                      <span className="text-secondary-700 ml-1">{note.objective}</span>
                    </div>
                    <div>
                      <span className="font-medium text-secondary-600">A:</span>
                      <span className="text-secondary-700 ml-1">{note.assessment}</span>
                    </div>
                    <div>
                      <span className="font-medium text-secondary-600">P:</span>
                      <span className="text-secondary-700 ml-1">{note.plan}</span>
                    </div>
                  </div>
                  {note.clinician_name && (
                    <div className="text-xs text-secondary-400 mt-2">
                      Recorded by: {note.clinician_name}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showAddModal && (
        <AddNoteModal
          patientId={selectedPatient || 0}
          onClose={() => setShowAddModal(false)}
        />
      )}
    </div>
  );
};

export default ClinicalNotes;
