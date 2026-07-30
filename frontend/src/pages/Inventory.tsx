import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import api from '../api/client';
import { SkeletonTable, SkeletonText } from '../components/Skeleton';
import { EmptyState } from '../components/EmptyState';
import AddInventoryModal from '../components/AddInventoryModal';
import { useToast } from '../context/ToastContext';

const fetchInventory = async () => {
  const { data } = await api.get('/inventory/');
  return data;
};

const deleteItem = async (id: number) => {
  await api.delete(`/inventory/${id}/`);
};

const Inventory: React.FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  const { data: items, isLoading } = useQuery({
    queryKey: ['inventory'],
    queryFn: fetchInventory,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast.showToast('Item deleted successfully', 'success');
    },
    onError: () => toast.showToast('Failed to delete item', 'error'),
  });

  const filteredItems = items?.filter((item: any) => {
    const matchesSearch = item.name.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = categoryFilter ? item.category === categoryFilter : true;
    return matchesSearch && matchesCategory;
  });

  const lowStockItems = items?.filter((i: any) => i.current_stock <= i.reorder_level).length || 0;

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <SkeletonText width="w-32" className="mb-1" />
            <SkeletonText width="w-48" />
          </div>
          <SkeletonText width="w-32" className="h-8" />
        </div>
        <SkeletonTable rows={5} cols={5} />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
        <div>
          <h1 className="text-2xl font-bold text-secondary-800">Inventory</h1>
          <p className="text-sm text-secondary-500">Manage drugs, consumables, equipment, and services</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          <PlusIcon className="w-4 h-4" />
          Add Item
        </button>
      </div>

      {lowStockItems > 0 && (
        <div className="bg-warning-light border border-warning/20 p-3 rounded-lg flex items-center gap-2 text-sm text-warning-dark">
          <ExclamationTriangleIcon className="w-4 h-4" />
          <span>{lowStockItems} item(s) are running low on stock. Please restock soon.</span>
        </div>
      )}

      <div className="card p-3 flex flex-col sm:flex-row gap-3">
        <div className="flex-1 flex items-center gap-2 bg-secondary-50 border border-secondary-200 rounded-lg px-3 py-1.5">
          <MagnifyingGlassIcon className="w-4 h-4 text-secondary-400" />
          <input
            type="text"
            placeholder="Search by name..."
            className="bg-transparent border-none outline-none text-sm w-full"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          className="input-field max-w-xs"
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
        >
          <option value="">All Categories</option>
          <option value="DRUG">Drugs</option>
          <option value="CONSUMABLE">Consumables</option>
          <option value="EQUIPMENT">Equipment</option>
          <option value="SERVICE">Services</option>
        </select>
      </div>

      {filteredItems?.length === 0 ? (
        <EmptyState
          title="No inventory items"
          description="Start by adding your first item – drugs, consumables, equipment, or services."
          actionLabel="Add Item"
          onAction={() => setShowModal(true)}
          iconType="inbox"
        />
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Category</th>
                <th>Stock</th>
                <th>Unit Price (KES)</th>
                <th>Expiry</th>
                <th>Status</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems?.map((item: any) => {
                const isLowStock = item.current_stock <= item.reorder_level;
                const isExpiring = item.expiry_date && new Date(item.expiry_date) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
                return (
                  <tr key={item.id}>
                    <td className="font-medium text-secondary-800">{item.name}</td>
                    <td><span className="badge badge-draft">{item.category.toLowerCase()}</span></td>
                    <td className={isLowStock ? 'text-danger font-medium' : ''}>{item.current_stock}</td>
                    <td>{item.unit_price}</td>
                    <td>
                      {item.expiry_date ? new Date(item.expiry_date).toLocaleDateString() : '—'}
                      {isExpiring && <ExclamationTriangleIcon className="w-3 h-3 inline ml-1 text-danger" title="Expiring soon" />}
                    </td>
                    <td>
                      {isLowStock && <span className="badge badge-warning text-[10px]">Low stock</span>}
                      {isExpiring && <span className="badge badge-danger text-[10px] ml-1">Expiring</span>}
                      {!isLowStock && !isExpiring && <span className="badge badge-active text-[10px]">OK</span>}
                    </td>
                    <td className="text-right">
                      <div className="flex justify-end gap-2">
                        <button onClick={() => { setEditingItem(item); setShowModal(true); }} className="text-secondary-400 hover:text-primary-600 transition-colors" title="Edit">
                          <PencilIcon className="w-4 h-4" />
                        </button>
                        <button onClick={() => { if (window.confirm('Are you sure?')) deleteMutation.mutate(item.id); }} className="text-secondary-400 hover:text-danger transition-colors" title="Delete">
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {showModal && <AddInventoryModal onClose={() => { setShowModal(false); setEditingItem(null); }} item={editingItem} />}
    </div>
  );
};

export default Inventory;
