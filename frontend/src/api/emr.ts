import api from './client';

export interface Patient {
  id: number; patient_id?: string | null; first_name: string; last_name: string;
  date_of_birth: string; gender: string; phone: string; email?: string | null;
  address?: string | null; emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null; next_of_kin_relationship?: string | null;
  national_id?: string | null; hiv_status?: string | null; intake_date: string;
  status: 'registered' | 'active' | 'inactive' | 'discharged' | 'transferred';
  care_type?: 'inpatient' | 'outpatient' | 'day_patient' | 'new_referral';
  referring_doctor?: string | null; notes?: string | null;
  substance_use_history?: unknown; psychiatric_diagnosis?: string | null; medical_history?: string | null;
}

export interface Admission {
  id: number; admission_number: string; patient: number; intake_date: string;
  discharge_date?: string | null; room?: string; bed?: string; primary_diagnosis?: string;
  psychiatric_diagnosis?: string; substance_use_history?: unknown; medical_history?: string;
  status?: 'admitted' | 'discharged'; length_of_stay_days?: number; patient_name?: string;
}

export interface ClinicalNote {
  id: number; patient: number; admission?: number | null; author_name?: string;
  clinician?: number; date: string; subjective: string; objective: string;
  assessment: string; plan: string; version: number;
}

export interface TreatmentGoal {
  id: number; treatment_plan: number; description: string; target_date?: string | null;
  status: string; progress_percent: number; progress_note?: string;
}

export interface TreatmentPlan {
  id: number; patient: number; admission?: number | null; title: string;
  diagnosis_summary?: string; status: string; start_date: string; target_date?: string | null;
  goals?: TreatmentGoal[];
}

export const emrApi = {
  patients: () => api.get<Patient[] | { results: Patient[] }>('/patients/', { params: { page_size: 100 } }).then(({ data }) => Array.isArray(data) ? data : data.results),
  patient: (id: string) => api.get<Patient>(`/patients/${id}/`).then(({ data }) => data),
  createPatient: (values: Record<string, unknown>) => api.post<Patient>('/patients/', values).then(({ data }) => data),
  admissions: (patientId?: string) => api.get<Admission[]>('/admissions/', { params: patientId ? { patient: patientId } : undefined }).then(({ data }) => data),
  createAdmission: (values: Record<string, unknown>) => api.post<Admission>('/admissions/', values).then(({ data }) => data),
  dischargeAdmission: (id: number, reason: string) => api.post<Admission>(`/admissions/${id}/discharge/`, { reason }).then(({ data }) => data),
  notes: (patientId: string) => api.get<ClinicalNote[]>('/clinical-notes/', { params: { patient: patientId } }).then(({ data }) => data),
  createNote: (values: Record<string, unknown>) => api.post<ClinicalNote>('/clinical-notes/', values).then(({ data }) => data),
  plans: (patientId: string) => api.get<TreatmentPlan[]>('/treatment-plans/', { params: { patient: patientId } }).then(({ data }) => data),
  createPlan: (values: Record<string, unknown>) => api.post<TreatmentPlan>('/treatment-plans/', values).then(({ data }) => data),
  goals: (planId: number) => api.get<TreatmentGoal[]>('/treatment-goals/', { params: { treatment_plan: planId } }).then(({ data }) => data),
  createGoal: (values: Record<string, unknown>) => api.post<TreatmentGoal>('/treatment-goals/', values).then(({ data }) => data),
  updateGoal: (id: number, values: Partial<TreatmentGoal>) => api.patch<TreatmentGoal>(`/treatment-goals/${id}/`, values).then(({ data }) => data),
};
