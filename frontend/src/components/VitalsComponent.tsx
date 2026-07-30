import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  HeartIcon, 
  BeakerIcon, 
  DocumentTextIcon,
  PlusIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../api/client';

const fetchVitals = async (patientId: number) => {
  const { data } = await api.get(`/vitals/?patient=${patientId}`);
  return data;
};

const createVital = async (payload: any) => {
  const { data } = await api.post('/vitals/', payload);
  return data;
};

const VitalsComponent: React.FC<{ patientId: number }> = ({ patientId }) => {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    date_measured: new Date().toISOString().slice(0, 16),
    systolic_bp: '',
    diastolic_bp: '',
    heart_rate: '',
    respiratory_rate: '',
    temperature: '',
    oxygen_saturation: '',
    blood_sugar: '',
    pain_score: '',
    weight: '',
    height: '',
    notes: '',
  });
  const [error, setError] = useState('');

  const { data: vitals, isLoading } = useQuery({
    queryKey: ['vitals', patientId],
    queryFn: () => fetchVitals(patientId),
    enabled: !!patientId,
  });

  const mutation = useMutation({
    mutationFn: createVital,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vitals', patientId] });
      setShowForm(false);
      setFormData({
        date_measured: new Date().toISOString().slice(0, 16),
        systolic_bp: '',
        diastolic_bp: '',
        heart_rate: '',
        respiratory_rate: '',
        temperature: '',
        oxygen_saturation: '',
        blood_sugar: '',
        pain_score: '',
        weight: '',
        height: '',
        notes: '',
      });
    },
    onError: (error: any) => {
      setError(error.response?.data?.error || 'Failed to save vitals');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    const payload = {
      patient: patientId,
      date_measured: formData.date_measured,
      systolic_bp: formData.systolic_bp ? parseInt(formData.systolic_bp) : null,
      diastolic_bp: formData.diastolic_bp ? parseInt(formData.diastolic_bp) : null,
      heart_rate: formData.heart_rate ? parseInt(formData.heart_rate) : null,
      respiratory_rate: formData.respiratory_rate ? parseInt(formData.respiratory_rate) : null,
      temperature: formData.temperature ? parseFloat(formData.temperature) : null,
      oxygen_saturation: formData.oxygen_saturation ? parseInt(formData.oxygen_saturation) : null,
      blood_sugar: formData.blood_sugar ? parseFloat(formData.blood_sugar) : null,
      pain_score: formData.pain_score ? parseInt(formData.pain_score) : null,
      weight: formData.weight ? parseFloat(formData.weight) : null,
      height: formData.height ? parseFloat(formData.height) : null,
      notes: formData.notes,
    };
    mutation.mutate(payload);
  };

  const chartData = vitals?.map((v: any) => ({
    date: new Date(v.date_measured).toLocaleDateString(),
    systolic: v.systolic_bp,
    diastolic: v.diastolic_bp,
    heart_rate: v.heart_rate,
    temperature: v.temperature,
    oxygen: v.oxygen_saturation,
  })).reverse() || [];

  const latest = vitals && vitals.length > 0 ? vitals[0] : null;

  const isAbnormal = (field: string, value: any) => {
    if (value === null || value === undefined || value === '') return false;
    switch (field) {
      case 'systolic_bp': return value > 140 || value < 90;
      case 'diastolic_bp': return value > 90 || value < 60;
      case 'heart_rate': return value > 100 || value < 60;
      case 'temperature': return value > 37.5;
      case 'oxygen_saturation': return value < 95;
      default: return false;
    }
  };

  if (isLoading) return <div>Loading vitals...</div>;

  return (
    <div className="space-y-6">
      {latest && (
        <div className="bg-white p-4 rounded shadow">
          <h3 className="font-semibold mb-2 flex items-center gap-2">
            <HeartIcon className="w-4 h-4 text-red-500" />
            Latest Vitals
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {latest.systolic_bp && (
              <div>
                <span className="text-sm text-gray-500">BP</span>
                <p className={`font-medium ${isAbnormal('systolic_bp', latest.systolic_bp) || isAbnormal('diastolic_bp', latest.diastolic_bp) ? 'text-red-600' : ''}`}>
                  {latest.systolic_bp}/{latest.diastolic_bp} mmHg
                </p>
              </div>
            )}
            {latest.heart_rate && (
              <div>
                <span className="text-sm text-gray-500">Heart Rate</span>
                <p className={`font-medium ${isAbnormal('heart_rate', latest.heart_rate) ? 'text-red-600' : ''}`}>
                  {latest.heart_rate} bpm
                </p>
              </div>
            )}
            {latest.temperature && (
              <div>
                <span className="text-sm text-gray-500">Temp</span>
                <p className={`font-medium ${isAbnormal('temperature', latest.temperature) ? 'text-red-600' : ''}`}>
                  {latest.temperature} °C
                </p>
              </div>
            )}
            {latest.oxygen_saturation && (
              <div>
                <span className="text-sm text-gray-500">SpO2</span>
                <p className={`font-medium ${isAbnormal('oxygen_saturation', latest.oxygen_saturation) ? 'text-red-600' : ''}`}>
                  {latest.oxygen_saturation}%
                </p>
              </div>
            )}
          </div>
          <p className="text-xs text-gray-400 mt-2">Recorded: {new Date(latest.recorded_at).toLocaleString()}</p>
        </div>
      )}

      <button
        onClick={() => setShowForm(!showForm)}
        className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        <PlusIcon className="w-4 h-4" />
        {showForm ? 'Cancel' : 'Record Vitals'}
      </button>

      {showForm && (
        <div className="bg-white p-4 rounded shadow">
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium">Date & Time *</label>
              <input
                type="datetime-local"
                className="w-full border rounded px-3 py-2"
                value={formData.date_measured}
                onChange={(e) => setFormData({ ...formData, date_measured: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Systolic BP (mmHg)</label>
              <input
                type="number"
                className="w-full border rounded px-3 py-2"
                value={formData.systolic_bp}
                onChange={(e) => setFormData({ ...formData, systolic_bp: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Diastolic BP (mmHg)</label>
              <input
                type="number"
                className="w-full border rounded px-3 py-2"
                value={formData.diastolic_bp}
                onChange={(e) => setFormData({ ...formData, diastolic_bp: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Heart Rate (bpm)</label>
              <input
                type="number"
                className="w-full border rounded px-3 py-2"
                value={formData.heart_rate}
                onChange={(e) => setFormData({ ...formData, heart_rate: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Respiratory Rate (/min)</label>
              <input
                type="number"
                className="w-full border rounded px-3 py-2"
                value={formData.respiratory_rate}
                onChange={(e) => setFormData({ ...formData, respiratory_rate: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Temperature (°C)</label>
              <input
                type="number"
                step="0.1"
                className="w-full border rounded px-3 py-2"
                value={formData.temperature}
                onChange={(e) => setFormData({ ...formData, temperature: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Oxygen Saturation (%)</label>
              <input
                type="number"
                className="w-full border rounded px-3 py-2"
                value={formData.oxygen_saturation}
                onChange={(e) => setFormData({ ...formData, oxygen_saturation: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Blood Sugar (mmol/L)</label>
              <input
                type="number"
                step="0.1"
                className="w-full border rounded px-3 py-2"
                value={formData.blood_sugar}
                onChange={(e) => setFormData({ ...formData, blood_sugar: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Pain Score (0-10)</label>
              <input
                type="number"
                min="0"
                max="10"
                className="w-full border rounded px-3 py-2"
                value={formData.pain_score}
                onChange={(e) => setFormData({ ...formData, pain_score: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Weight (kg)</label>
              <input
                type="number"
                step="0.1"
                className="w-full border rounded px-3 py-2"
                value={formData.weight}
                onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Height (cm)</label>
              <input
                type="number"
                step="0.1"
                className="w-full border rounded px-3 py-2"
                value={formData.height}
                onChange={(e) => setFormData({ ...formData, height: e.target.value })}
              />
            </div>
            <div className="md:col-span-3">
              <label className="block text-sm font-medium">Notes</label>
              <textarea
                className="w-full border rounded px-3 py-2"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={2}
                placeholder="Additional notes..."
              />
            </div>
            {error && (
              <div className="md:col-span-3 text-red-600 text-sm flex items-center gap-2">
                <ExclamationTriangleIcon className="w-4 h-4" />
                {error}
              </div>
            )}
            <div className="md:col-span-3 flex gap-2">
              <button
                type="submit"
                disabled={mutation.isPending}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {mutation.isPending ? 'Saving...' : 'Save Vitals'}
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {vitals && vitals.length > 0 && (
        <div className="bg-white p-4 rounded shadow">
          <h3 className="font-semibold mb-2 flex items-center gap-2">
            <DocumentTextIcon className="w-4 h-4" />
            Vitals History
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left">Date</th>
                  <th className="px-3 py-2 text-left">BP</th>
                  <th className="px-3 py-2 text-left">HR</th>
                  <th className="px-3 py-2 text-left">Temp</th>
                  <th className="px-3 py-2 text-left">SpO2</th>
                  <th className="px-3 py-2 text-left">Pain</th>
                  <th className="px-3 py-2 text-left">BMI</th>
                  <th className="px-3 py-2 text-left">Recorded By</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {vitals.map((v: any) => (
                  <tr key={v.id}>
                    <td className="px-3 py-2">{new Date(v.date_measured).toLocaleString()}</td>
                    <td className={`px-3 py-2 ${isAbnormal('systolic_bp', v.systolic_bp) || isAbnormal('diastolic_bp', v.diastolic_bp) ? 'text-red-600 font-medium' : ''}`}>
                      {v.systolic_bp}/{v.diastolic_bp}
                    </td>
                    <td className={`px-3 py-2 ${isAbnormal('heart_rate', v.heart_rate) ? 'text-red-600 font-medium' : ''}`}>
                      {v.heart_rate}
                    </td>
                    <td className={`px-3 py-2 ${isAbnormal('temperature', v.temperature) ? 'text-red-600 font-medium' : ''}`}>
                      {v.temperature}
                    </td>
                    <td className={`px-3 py-2 ${isAbnormal('oxygen_saturation', v.oxygen_saturation) ? 'text-red-600 font-medium' : ''}`}>
                      {v.oxygen_saturation}%
                    </td>
                    <td className="px-3 py-2">{v.pain_score}</td>
                    <td className="px-3 py-2">{v.bmi ? v.bmi.toFixed(1) : '-'}</td>
                    <td className="px-3 py-2">{v.recorded_by_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {chartData.length > 1 && (
        <div className="bg-white p-4 rounded shadow">
          <h3 className="font-semibold mb-2 flex items-center gap-2">
            <BeakerIcon className="w-4 h-4" />
            Trends
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="systolic" stroke="#2563EB" name="Systolic BP" />
              <Line type="monotone" dataKey="diastolic" stroke="#10B981" name="Diastolic BP" />
              <Line type="monotone" dataKey="heart_rate" stroke="#EF4444" name="Heart Rate" />
              <Line type="monotone" dataKey="temperature" stroke="#F59E0B" name="Temp" />
              <Line type="monotone" dataKey="oxygen" stroke="#8B5CF6" name="SpO2" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default VitalsComponent;
