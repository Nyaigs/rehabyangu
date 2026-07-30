import React from 'react';
import { PlusIcon, InboxIcon } from '@heroicons/react/24/outline';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
  iconType?: 'inbox' | 'search' | 'users' | 'documents';
}

const iconMap = {
  inbox: InboxIcon,
  search: InboxIcon,
  users: InboxIcon,
  documents: InboxIcon,
};

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon,
  actionLabel,
  onAction,
  iconType = 'inbox',
}) => {
  const Icon = icon || iconMap[iconType] || InboxIcon;

  return (
    <div className="flex flex-col items-center justify-center text-center py-16 px-4">
      <div className="w-16 h-16 bg-secondary-100 rounded-full flex items-center justify-center mb-4">
        <Icon className="w-8 h-8 text-secondary-400" />
      </div>
      <h3 className="text-lg font-medium text-secondary-800 mb-1">{title}</h3>
      <p className="text-sm text-secondary-500 max-w-sm">{description}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="mt-4 btn-primary text-sm"
        >
          <PlusIcon className="w-4 h-4" />
          {actionLabel}
        </button>
      )}
    </div>
  );
};
