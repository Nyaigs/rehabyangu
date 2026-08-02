import { InputHTMLAttributes, ReactNode, forwardRef, useId } from "react";

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  /** Icon rendered inside the input's left edge (e.g. envelope, lock) */
  leadingIcon?: ReactNode;
  /** Interactive control rendered at the input's right edge (e.g. show/hide password) */
  trailingAction?: ReactNode;
}

/**
 * Input focus uses a soft border-color + ring transition only — no glow,
 * no scale — matching the "soft border transition" spec and keeping the
 * form calm and clinical rather than playful.
 */
export const TextField = forwardRef<HTMLInputElement, TextFieldProps>(
  (
    { label, error, leadingIcon, trailingAction, id, className = "", ...props },
    ref
  ) => {
    const generatedId = useId();
    const inputId = id ?? generatedId;
    const errorId = `${inputId}-error`;

    return (
      <div className="flex flex-col gap-1">
        <label
          htmlFor={inputId}
          className="text-secondary font-medium text-ink-secondary"
        >
          {label}
        </label>

        <div className="relative flex items-center">
          {leadingIcon && (
            <span
              className="pointer-events-none absolute left-3 flex h-5 w-5 items-center justify-center text-ink-muted"
              aria-hidden="true"
            >
              {leadingIcon}
            </span>
          )}

          <input
            id={inputId}
            ref={ref}
            aria-invalid={Boolean(error)}
            aria-describedby={error ? errorId : undefined}
            className={`
              w-full rounded-lg border bg-surface py-3 text-body text-ink-primary
              placeholder:text-ink-muted
              transition-colors duration-150 ease-out
              focus:outline-none focus:ring-2 focus:ring-primary/20
              disabled:bg-background disabled:text-ink-muted
              ${leadingIcon ? "pl-10" : "pl-3"}
              ${trailingAction ? "pr-10" : "pr-3"}
              ${error ? "border-danger focus:border-danger" : "border-border focus:border-primary"}
              ${className}
            `}
            {...props}
          />

          {trailingAction && (
            <span className="absolute right-2 flex items-center">{trailingAction}</span>
          )}
        </div>

        {error && (
          <p id={errorId} role="alert" className="text-secondary text-danger">
            {error}
          </p>
        )}
      </div>
    );
  }
);

TextField.displayName = "TextField";
