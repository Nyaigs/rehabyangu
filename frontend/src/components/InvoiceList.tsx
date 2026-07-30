import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  DocumentArrowDownIcon,
  EnvelopeIcon,
  PlusIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  ShareIcon,
} from '@heroicons/react/24/outline';
import api from '../api/client';
import { useToast } from '../context/ToastContext';

interface InvoiceListProps {
  patientId: number;
}

const fetchInvoices = async (patientId: number) => {
  const { data } = await api.get(`/invoices/?patient=${patientId}`);
  return data;
};

const generateInvoice = async (payload: any) => {
  const { data } = await api.post('/invoices/generate/', payload);
  return data;
};

const downloadInvoice = async (id: number) => {
  const response = await api.get(`/invoices/${id}/download/`, { responseType: 'blob' });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `invoice-${id}.pdf`);
  document.body.appendChild(link);
  link.click();
  link.remove();
};

const sendInvoiceEmail = async (id: number, email: string) => {
  const { data } = await api.post(`/invoices/${id}/send-email/`, { email });
  return data;
};

const InvoiceList: React.FC<InvoiceListProps> = ({ patientId }) => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [formData, setFormData] = useState({
    cover_letter: '',
    sponsor_email: '',
    sponsor_name: '',
    sponsor_phone: '',
    due_date: '',
    period_start: '',
    period_end: '',
  });
  const [error, setError] = useState('');

  const { data: invoices, isLoading, refetch } = useQuery({
    queryKey: ['invoices', patientId],
    queryFn: () => fetchInvoices(patientId),
    enabled: !!patientId,
  });

  const generateMutation = useMutation({
    mutationFn: generateInvoice,
    onSuccess: () => {
      refetch();
      setShowGenerateModal(false);
      setFormData({
        cover_letter: '',
        sponsor_email: '',
        sponsor_name: '',
        sponsor_phone: '',
        due_date: '',
        period_start: '',
        period_end: '',
      });
      toast.showToast('Invoice generated successfully!', 'success');
    },
    onError: (error: any) => {
      setError(error.response?.data?.error || 'Failed to generate invoice');
      toast.showToast('Failed to generate invoice', 'error');
    },
  });

  const sendEmailMutation = useMutation({
    mutationFn: ({ id, email }: { id: number; email: string }) => sendInvoiceEmail(id, email),
    onSuccess: () => {
      refetch();
      toast.showToast('Invoice sent via email.', 'success');
    },
    onError: (error: any) => {
      toast.showToast(error.response?.data?.error || 'Failed to send email', 'error');
    },
  });

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    const payload = {
      patient_id: patientId,
      ...formData,
    };
    generateMutation.mutate(payload);
  };

  const handleSendEmail = (id: number, currentEmail: string) => {
    const email = prompt('Enter sponsor email address:', currentEmail || '');
    if (email) {
      sendEmailMutation.mutate({ id, email });
    }
  };

  // ----- WhatsApp sharing -----
  const handleShareWhatsApp = (invoice: any) => {
    const token = invoice.download_token;
    if (!token) {
      toast.showToast('No download token available for this invoice.', 'error');
      return;
    }
    const baseUrl = window.location.origin;
    const downloadLink = `${baseUrl}/invoice/download/${token}/`;
    const message = `Your invoice ${invoice.invoice_number} for patient ${invoice.patient_name} is ready.\n\nAmount: KES ${invoice.total_amount}\nDue Date: ${new Date(invoice.due_date).toLocaleDateString()}\n\nDownload: ${downloadLink}`;
    const phone = invoice.sponsor_phone || prompt('Enter sponsor phone number (e.g., 254795183600):');
    if (!phone) return;
    const cleanPhone = phone.replace(/^\+?0?/, '');
    const waUrl = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(message)}`;
    window.open(waUrl, '_blank');
  };

  if (isLoading) return <div className="text-sm text-secondary-500">Loading invoices...</div>;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-secondary-800">Invoices</h3>
        <button
          onClick={() => setShowGenerateModal(true)}
          className="btn-primary text-sm"
        >
          <PlusIcon className="w-4 h-4" />
          Generate Invoice
        </button>
      </div>

      {invoices?.length === 0 ? (
        <p className="text-secondary-500">No invoices generated yet.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Invoice</th>
                <th>Date</th>
                <th>Due Date</th>
                <th>Total</th>
                <th>Status</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {invoices?.map((inv: any) => (
                <tr key={inv.id}>
                  <td className="font-mono text-xs">{inv.invoice_number}</td>
                  <td>{new Date(inv.generated_at).toLocaleDateString()}</td>
                  <td>{new Date(inv.due_date).toLocaleDateString()}</td>
                  <td className="font-medium">KES {inv.total_amount}</td>
                  <td>
                    <span className={`badge ${
                      inv.status === 'draft' ? 'badge-draft' :
                      inv.status === 'sent' ? 'badge-sent' :
                      inv.status === 'paid' ? 'badge-paid' :
                      inv.status === 'overdue' ? 'badge-overdue' : ''
                    }`}>
                      {inv.status}
                    </span>
                  </td>
                  <td className="text-right">
                    <div className="flex flex-wrap justify-end gap-1">
                      <button
                        onClick={() => downloadInvoice(inv.id)}
                        className="text-secondary-400 hover:text-primary-600 transition-colors"
                        title="Download PDF"
                      >
                        <DocumentArrowDownIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleSendEmail(inv.id, inv.sponsor_email)}
                        className="text-secondary-400 hover:text-primary-600 transition-colors"
                        title="Send via Email"
                      >
                        <EnvelopeIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleShareWhatsApp(inv)}
                        className="text-secondary-400 hover:text-green-600 transition-colors"
                        title="Send via WhatsApp"
                      >
                        <ShareIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showGenerateModal && (
        <div className="modal-overlay" onClick={() => setShowGenerateModal(false)}>
          <div className="modal-content animate-scaleIn" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-secondary-800">Generate Invoice</h2>
              <button onClick={() => setShowGenerateModal(false)} className="text-secondary-400 hover:text-secondary-600">
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleGenerate}>
              <div className="space-y-3">
                <div>
                  <label className="form-label">Cover Letter (optional)</label>
                  <textarea
                    className="input-field"
                    value={formData.cover_letter}
                    onChange={(e) => setFormData({ ...formData, cover_letter: e.target.value })}
                    rows={3}
                    placeholder="Thank you for your continued support..."
                  />
                </div>
                <div>
                  <label className="form-label">Sponsor Name</label>
                  <input
                    type="text"
                    className="input-field"
                    value={formData.sponsor_name}
                    onChange={(e) => setFormData({ ...formData, sponsor_name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="form-label">Sponsor Email</label>
                  <input
                    type="email"
                    className="input-field"
                    value={formData.sponsor_email}
                    onChange={(e) => setFormData({ ...formData, sponsor_email: e.target.value })}
                  />
                </div>
                <div>
                  <label className="form-label">Sponsor Phone (for WhatsApp)</label>
                  <input
                    type="text"
                    className="input-field"
                    value={formData.sponsor_phone}
                    onChange={(e) => setFormData({ ...formData, sponsor_phone: e.target.value })}
                    placeholder="e.g. 254795183600"
                  />
                </div>
                <div>
                  <label className="form-label">Due Date</label>
                  <input
                    type="date"
                    className="input-field"
                    value={formData.due_date}
                    onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                  />
                </div>
                <div>
                  <label className="form-label">Period Start</label>
                  <input
                    type="date"
                    className="input-field"
                    value={formData.period_start}
                    onChange={(e) => setFormData({ ...formData, period_start: e.target.value })}
                  />
                </div>
                <div>
                  <label className="form-label">Period End</label>
                  <input
                    type="date"
                    className="input-field"
                    value={formData.period_end}
                    onChange={(e) => setFormData({ ...formData, period_end: e.target.value })}
                  />
                </div>
                {error && <p className="text-danger text-sm flex items-center gap-1">
                  <ExclamationTriangleIcon className="w-4 h-4" />
                  {error}
                </p>}
                <button
                  type="submit"
                  disabled={generateMutation.isPending}
                  className="btn-primary w-full justify-center"
                >
                  {generateMutation.isPending ? 'Generating...' : 'Generate Invoice'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default InvoiceList;
