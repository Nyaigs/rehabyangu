import React from 'react';
import { PlusIcon, InboxIcon } from '@heroicons/react/24/outline';
import { Button } from './ui/Button';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: React.ElementType;
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
    <div className="flex flex-col items-center justify-center px-4 py-16 text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary-subtle">
        <Icon className="h-8 w-8 text-primary" />
      </div>
      <h3 className="mb-1 text-component-title text-ink-primary">{title}</h3>
      <p className="max-w-sm text-secondary text-ink-secondary">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} className="mt-6 w-auto">
          <PlusIcon className="w-4 h-4" />
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
