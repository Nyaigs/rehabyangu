import { forwardRef, useId, type InputHTMLAttributes, type SelectHTMLAttributes, type TextareaHTMLAttributes } from 'react';
import { Input } from './input';

type Shared = { label: string; error?: string };

export const Field = forwardRef<HTMLInputElement, Shared & InputHTMLAttributes<HTMLInputElement>>(({ label, error, id, className = '', ...props }, ref) => {
  const generated = useId(); const fieldId = id || generated;
  return <div className="space-y-1.5"><label htmlFor={fieldId} className="form-label">{label}</label><Input id={fieldId} ref={ref} aria-invalid={!!error} aria-describedby={error ? `${fieldId}-error` : undefined} className={className} {...props} />{error && <p id={`${fieldId}-error`} className="text-caption text-danger" role="alert">{error}</p>}</div>;
});
Field.displayName = 'Field';

export const SelectField = forwardRef<HTMLSelectElement, Shared & SelectHTMLAttributes<HTMLSelectElement>>(({ label, error, id, children, className = '', ...props }, ref) => {
  const generated = useId(); const fieldId = id || generated;
  return <div className="space-y-1.5"><label htmlFor={fieldId} className="form-label">{label}</label><select id={fieldId} ref={ref} aria-invalid={!!error} aria-describedby={error ? `${fieldId}-error` : undefined} className={`input-field ${className}`} {...props}>{children}</select>{error && <p id={`${fieldId}-error`} className="text-caption text-danger" role="alert">{error}</p>}</div>;
});
SelectField.displayName = 'SelectField';

export const TextareaField = forwardRef<HTMLTextAreaElement, Shared & TextareaHTMLAttributes<HTMLTextAreaElement>>(({ label, error, id, className = '', ...props }, ref) => {
  const generated = useId(); const fieldId = id || generated;
  return <div className="space-y-1.5"><label htmlFor={fieldId} className="form-label">{label}</label><textarea id={fieldId} ref={ref} aria-invalid={!!error} aria-describedby={error ? `${fieldId}-error` : undefined} className={`input-field min-h-24 ${className}`} {...props} />{error && <p id={`${fieldId}-error`} className="text-caption text-danger" role="alert">{error}</p>}</div>;
});
TextareaField.displayName = 'TextareaField';
