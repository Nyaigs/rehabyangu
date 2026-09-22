import * as Dialog from '@radix-ui/react-dialog';
import type { ReactNode } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

export function Modal({ open, onOpenChange, title, children }: { open: boolean; onOpenChange: (open: boolean) => void; title: string; children: ReactNode }) {
  return <Dialog.Root open={open} onOpenChange={onOpenChange}><Dialog.Portal><Dialog.Overlay className="fixed inset-0 z-40 bg-slate-950/45" /><Dialog.Content className="fixed left-1/2 top-1/2 z-50 max-h-[calc(100dvh-2rem)] w-[calc(100%-2rem)] max-w-xl -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-card border border-border bg-surface p-5 shadow-modal sm:p-6"><div className="mb-6 flex items-center justify-between gap-4"><Dialog.Title className="text-component-title text-ink-primary">{title}</Dialog.Title><Dialog.Close aria-label="Close dialog" className="grid h-11 w-11 shrink-0 place-items-center rounded-btn text-ink-secondary hover:bg-secondary-100 hover:text-ink-primary"><XMarkIcon className="h-5 w-5" /></Dialog.Close></div>{children}</Dialog.Content></Dialog.Portal></Dialog.Root>;
}
