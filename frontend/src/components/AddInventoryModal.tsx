import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { XMarkIcon } from '@heroicons/react/24/outline';
import api from '../api/client';
import { useToast } from '../context/ToastContext';

const inventorySchema = z.object({
  name: z.string().min(1, 'Name is required'),
  category: z.enum(['DRUG', 'CONSUMABLE', 'EQUIPMENT', 'SERVICE']),
  cost_price: z.number().min(0, 'Cost price must be 0 or more'),
  unit_price: z.number().min(0, 'Unit price must be 0 or more'),
  current_stock: z.number().int().min(0, 'Stock must be 0 or more'),
  reorder_level: z.number().int().min(0, 'Reorder level must be 0 or more'),
  expiry_date: z.string().optional(),
});

type InventoryFormInputs = z.infer<typeof inventorySchema>;

interface AddInventoryModalProps {
  onClose: () => void;
  item?: any; // if editing, pass the item data
}

const AddInventoryModal: React.FC<AddInventoryModalProps> = ({ onClose, item }) => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const isEditing = !!item;

  const { register, handleSubmit, formState: { errors, isSubmitting }, reset } = useForm<InventoryFormInputs>({
    resolver: zodResolver(inventorySchema),
    defaultValues: isEditing ? {
      name: item.name,
      category: item.category,
      cost_price: parseFloat(item.cost_price),
      unit_price: parseFloat(item.unit_price),
      current_stock: item.current_stock,
      reorder_level: item.reorder_level,
      expiry_date: item.expiry_date || '',
    } : {
      category: 'DRUG',
      cost_price: 0,
      unit_price: 0,
      current_stock: 0,
      reorder_level: 10,
    },
  });

  const mutation = useMutation({
    mutationFn: (data: InventoryFormInputs) => {
      const payload = { ...data };
      if (payload.expiry_date === '') delete payload.expiry_date;
      if (isEditing) {
        return api.patch(`/inventory/${item.id}/`, payload);
      }
      return api.post('/inventory/', payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast.showToast(isEditing ? 'Item updated successfully!' : 'Item added successfully!', 'success');
      reset();
      onClose();
    },
    onError: (error: any) => {
      toast.showToast(error.response?.data?.error || 'Failed to save item', 'error');
    },
  });

  const onSubmit = (data: InventoryFormInputs) => mutation.mutate(data);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content animate-scaleIn" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-lg font-semibold text-secondary-800">
            {isEditing ? 'Edit Inventory Item' : 'Add Inventory Item'}
          </h2>
          <button onClick={onClose} className="text-secondary-400 hover:text-secondary-600">
            <XMarkIcon className="w-4 h-4" />
          </button>
        </div>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-3">
            <div>
              <label className="form-label">Name *</label>
              <input
                {...register('name')}
                className={`input-field ${errors.name ? 'input-error' : ''}`}
                placeholder="e.g. Paracetamol 500mg"
              />
              {errors.name && <p className="text-xs text-red-600 mt-1">{errors.name.message}</p>}
            </div>
            <div>
              <label className="form-label">Category *</label>
              <select {...register('category')} className="input-field">
                <option value="DRUG">Drug/Medication</option>
                <option value="CONSUMABLE">Consumable</option>
                <option value="EQUIPMENT">Medical Equipment</option>
                <option value="SERVICE">Rehab Service</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="form-label">Cost Price (KES)</label>
                <input
                  type="number"
                  step="0.01"
                  {...register('cost_price', { valueAsNumber: true })}
                  className={`input-field ${errors.cost_price ? 'input-error' : ''}`}
                />
                {errors.cost_price && <p className="text-xs text-red-600 mt-1">{errors.cost_price.message}</p>}
              </div>
              <div>
                <label className="form-label">Unit Price (KES) *</label>
                <input
                  type="number"
                  step="0.01"
                  {...register('unit_price', { valueAsNumber: true })}
                  className={`input-field ${errors.unit_price ? 'input-error' : ''}`}
                />
                {errors.unit_price && <p className="text-xs text-red-600 mt-1">{errors.unit_price.message}</p>}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="form-label">Current Stock *</label>
                <input
                  type="number"
                  {...register('current_stock', { valueAsNumber: true })}
                  className={`input-field ${errors.current_stock ? 'input-error' : ''}`}
                />
                {errors.current_stock && <p className="text-xs text-red-600 mt-1">{errors.current_stock.message}</p>}
              </div>
              <div>
                <label className="form-label">Reorder Level *</label>
                <input
                  type="number"
                  {...register('reorder_level', { valueAsNumber: true })}
                  className={`input-field ${errors.reorder_level ? 'input-error' : ''}`}
                />
                {errors.reorder_level && <p className="text-xs text-red-600 mt-1">{errors.reorder_level.message}</p>}
              </div>
            </div>
            <div>
              <label className="form-label">Expiry Date (optional)</label>
              <input
                type="date"
                {...register('expiry_date')}
                className="input-field"
              />
            </div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-primary w-full justify-center"
            >
              {isSubmitting ? 'Saving...' : isEditing ? 'Update Item' : 'Add Item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddInventoryModal;
