import type { ReactNode } from 'react';

export function Table({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className="overflow-x-auto rounded-card border border-border bg-surface shadow-card"><table className={`w-full min-w-[640px] text-left text-secondary text-ink-secondary ${className}`}>{children}</table></div>;
}

export function EmptyTable({ colSpan, children }: { colSpan: number; children: ReactNode }) {
  return <tr><td colSpan={colSpan} className="p-8 text-center text-secondary text-ink-secondary">{children}</td></tr>;
}
