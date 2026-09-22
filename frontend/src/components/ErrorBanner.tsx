import type { ReactNode } from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

export function ErrorBanner({ children, onRetry }: { children: ReactNode; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex items-start justify-between gap-4 rounded-card border border-danger/25 bg-danger-subtle p-4 text-secondary text-danger">
      <div className="flex gap-3"><ExclamationTriangleIcon className="mt-0.5 h-5 w-5 shrink-0" />{children}</div>
      {onRetry && <button type="button" onClick={onRetry} className="min-h-11 shrink-0 px-2 font-semibold underline underline-offset-2">Try again</button>}
    </div>
  );
}
