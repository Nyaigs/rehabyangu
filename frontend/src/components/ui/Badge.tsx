import type { ReactNode } from 'react';

type Tone = 'neutral' | 'success' | 'warning' | 'danger' | 'info';
const tones: Record<Tone, string> = {
  neutral: 'bg-secondary-100 text-secondary-700', success: 'bg-accent-subtle text-accent-700',
  warning: 'bg-warning-subtle text-warning', danger: 'bg-danger-subtle text-danger', info: 'bg-primary-subtle text-primary-700',
};

export function Badge({ children, tone = 'neutral' }: { children: ReactNode; tone?: Tone }) {
  return <span className={`inline-flex min-h-6 items-center rounded-full px-2.5 py-1 text-caption normal-case tracking-normal ${tones[tone]}`}>{children}</span>;
}
