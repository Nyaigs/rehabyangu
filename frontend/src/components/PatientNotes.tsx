import React, { useState } from 'react';
import { usePatientNotes } from '../hooks/usePatientNotes';
import NoteForm from './NoteForm';

interface Props {
  patientId: number;
}

const PatientNotes: React.FC<Props> = ({ patientId }) => {
  const [showForm, setShowForm] = useState(false);
  const { data: notes, isLoading, error } = usePatientNotes(patientId);

  if (isLoading) return <div>Loading notes...</div>;
  if (error) return <div className="text-red-500">Error loading notes</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Clinical Notes</h3>
        <button onClick={() => setShowForm(true)} className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
          + Add Note
        </button>
      </div>
      {notes?.length === 0 ? (
        <p className="text-gray-500">No notes recorded yet.</p>
      ) : (
        <div className="space-y-4">
          {notes?.map((note: any) => (
            <div key={note.id} className="bg-gray-50 p-4 rounded border">
              <div className="flex justify-between text-sm text-gray-500 mb-2">
                <span>Dr. {note.clinician_name || note.clinician}</span>
                <span>{new Date(note.date).toLocaleString()}</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div><span className="font-medium">S:</span> {note.subjective}</div>
                <div><span className="font-medium">O:</span> {note.objective}</div>
                <div><span className="font-medium">A:</span> {note.assessment}</div>
                <div><span className="font-medium">P:</span> {note.plan}</div>
              </div>
            </div>
          ))}
        </div>
      )}
      {showForm && <NoteForm patientId={patientId} onClose={() => setShowForm(false)} />}
    </div>
  );
};

export default PatientNotes;
