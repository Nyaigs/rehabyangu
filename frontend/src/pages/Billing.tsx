import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  BeakerIcon,
  ClipboardDocumentListIcon,
  WrenchScrewdriverIcon,
  HeartIcon,
  InformationCircleIcon,
  DocumentTextIcon,
  PlusIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';
import api from '../api/client';
import InvoiceList from '../components/InvoiceList';
import { useToast } from '../context/ToastContext';
import { EmptyState } from '../components/EmptyState';
import { SkeletonText } from '../components/Skeleton';

const fetchPatients = async () => {
  const { data } = await api.get('/patients/');
  return data;
};

const fetchInventory = async () => {
  const { data } = await api.get('/inventory/');
  return data;
};

const fetchPatientBill = async (patientId: number) => {
  const { data } = await api.get(`/patient-bill/${patientId}/`);
  return data;
};

const Billing: React.FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [selectedPatient, setSelectedPatient] = useState<number | null>(null);
  const [selectedItem, setSelectedItem] = useState<number | null>(null);
  const [quantity, setQuantity] = useState<number>(1);
  const [activeTab, setActiveTab] = useState<'charges' | 'invoices'>('charges');

  const { data: patients, isLoading: patientsLoading } = useQuery({ queryKey: ['patients'], queryFn: fetchPatients });
  const { data: inventory, isLoading: inventoryLoading } = useQuery({ queryKey: ['inventory'], queryFn: fetchInventory });
  const { data: bill, refetch: refetchBill } = useQuery({
    queryKey: ['patient-bill', selectedPatient],
    queryFn: () => fetchPatientBill(selectedPatient!),
    enabled: !!selectedPatient,
  });

  const mutation = useMutation({
    mutationFn: async () => {
      if (!selectedPatient || !selectedItem || quantity <= 0) throw new Error('Invalid input');
      const response = await api.post('/charge/', {
        patient_id: selectedPatient,
        item_id: selectedItem,
        quantity: quantity,
      });
      return response.data;
    },
    onSuccess: () => {
      refetchBill();
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast.showToast('Charge applied successfully!', 'success');
    },
    onError: (error: any) => {
      toast.showToast(error.response?.data?.error || 'Failed to charge patient', 'error');
    },
  });

  const handleCharge = () => {
    if (!selectedPatient || !selectedItem || quantity <= 0) {
      toast.showToast('Please select patient, item, and quantity', 'warning');
      return;
    }
    mutation.mutate();
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'DRUG': return BeakerIcon;
      case 'CONSUMABLE': return ClipboardDocumentListIcon;
      case 'EQUIPMENT': return WrenchScrewdriverIcon;
      case 'SERVICE': return HeartIcon;
      default: return ClipboardDocumentListIcon;
    }
  };
  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'DRUG': return 'Drug';
      case 'CONSUMABLE': return 'Consumable';
      case 'EQUIPMENT': return 'Equipment';
      case 'SERVICE': return 'Service';
      default: return 'Item';
    }
  };

  const getItemOptionLabel = (item: any) => {
    const categoryLabel = getCategoryLabel(item.category);
    if (item.category === 'SERVICE') {
      return `${categoryLabel}: ${item.name} (KES ${item.unit_price})`;
    }
    return `${categoryLabel}: ${item.name} (Stock: ${item.current_stock}, KES ${item.unit_price})`;
  };

  const selectedItemData = inventory?.find((i: any) => i.id === selectedItem);

  if (patientsLoading || inventoryLoading) {
    return (
      <div className="space-y-4">
        <SkeletonText width="w-48" className="mb-1" />
        <SkeletonText width="w-64" />
        <div className="card p-4"><SkeletonText width="w-full" className="h-8" /></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-secondary-800">Billing & Charges</h1>
        <p className="text-sm text-secondary-500">Manage patient charges, invoices, and payments</p>
      </div>

      <div className="card p-4">
        <label className="form-label">Select Patient</label>
        <select
          className="input-field max-w-md"
          value={selectedPatient || ''}
          onChange={(e) => setSelectedPatient(Number(e.target.value))}
        >
          <option value="">Select patient</option>
          {patients?.map((p: any) => (
            <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
          ))}
        </select>
        {bill && (
          <div className="mt-2 text-sm font-medium">
            Current Balance: <span className="text-primary-600">KES {bill.total_balance}</span>
          </div>
        )}
      </div>

      {selectedPatient && (
        <>
          <div className="border-b border-secondary-200">
            <div className="flex gap-4">
              <button
                onClick={() => setActiveTab('charges')}
                className={`pb-2 px-2 text-sm font-medium flex items-center gap-1.5 ${
                  activeTab === 'charges' ? 'border-b-2 border-primary-600 text-primary-700' : 'text-secondary-500 hover:text-secondary-700'
                }`}
              >
                <PlusIcon className="w-4 h-4" />
                Charges
              </button>
              <button
                onClick={() => setActiveTab('invoices')}
                className={`pb-2 px-2 text-sm font-medium flex items-center gap-1.5 ${
                  activeTab === 'invoices' ? 'border-b-2 border-primary-600 text-primary-700' : 'text-secondary-500 hover:text-secondary-700'
                }`}
              >
                <DocumentTextIcon className="w-4 h-4" />
                Invoices
              </button>
            </div>
          </div>

          {activeTab === 'charges' && (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg flex items-start gap-3 text-sm text-blue-800">
                <InformationCircleIcon className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <p><strong>Services</strong> do not deduct stock. Only physical items reduce inventory.</p>
              </div>

              <div className="card p-4 max-w-xl">
                <div className="space-y-4">
                  <div>
                    <label className="form-label">Item / Service</label>
                    <select
                      className="input-field"
                      value={selectedItem || ''}
                      onChange={(e) => setSelectedItem(Number(e.target.value))}
                    >
                      <option value="">Select item or service</option>
                      {inventory?.map((item: any) => (
                        <option key={item.id} value={item.id}>
                          {getItemOptionLabel(item)}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="form-label">Quantity</label>
                    <input
                      type="number"
                      className="input-field"
                      value={quantity}
                      onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                      min="1"
                    />
                    {selectedItemData?.category === 'SERVICE' && (
                      <p className="text-xs text-secondary-500 mt-1">Services do not affect stock levels.</p>
                    )}
                  </div>

                  <button
                    onClick={handleCharge}
                    disabled={mutation.isPending}
                    className="btn-primary w-full justify-center"
                  >
                    {mutation.isPending ? <><ArrowPathIcon className="w-4 h-4 animate-spin" /> Processing</> : 'Charge Patient'}
                  </button>
                </div>
              </div>

              {bill && bill.items && bill.items.length > 0 ? (
                <div className="card p-4">
                  <h3 className="text-sm font-semibold text-secondary-700 mb-3">Recent Charges</h3>
                  <ul className="divide-y divide-secondary-100">
                    {bill.items.slice().reverse().map((item: any) => {
                      const Icon = getCategoryIcon(item.category || '');
                      return (
                        <li key={item.id} className="py-2 flex justify-between items-center">
                          <div className="flex items-center gap-2">
                            <Icon className="w-4 h-4 text-secondary-400" />
                            <span className="font-medium text-secondary-800">{item.item_name}</span>
                            <span className="badge badge-draft text-[10px]">{getCategoryLabel(item.category || '')}</span>
                            <span className="text-xs text-secondary-500">x{item.quantity}</span>
                          </div>
                          <span className="font-medium text-secondary-800">KES {item.subtotal}</span>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ) : (
                <EmptyState title="No charges yet" description="Select a patient and charge an item." iconType="inbox" />
              )}
            </div>
          )}

          {activeTab === 'invoices' && <InvoiceList patientId={selectedPatient} />}
        </>
      )}
    </div>
  );
};

export default Billing;
