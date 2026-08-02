import { InputHTMLAttributes, forwardRef, useId } from "react";
import { CheckIcon } from "@heroicons/react/24/solid";

interface CheckboxProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, id, className = "", ...props }, ref) => {
    const generatedId = useId();
    const inputId = id ?? generatedId;

    return (
      <label
        htmlFor={inputId}
        className="inline-flex cursor-pointer select-none items-center gap-2"
      >
        <span className="relative flex h-[18px] w-[18px] items-center justify-center">
          <input
            id={inputId}
            ref={ref}
            type="checkbox"
            className={`peer h-[18px] w-[18px] cursor-pointer appearance-none rounded border border-border-strong bg-surface transition-colors duration-150 checked:border-primary checked:bg-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary ${className}`}
            {...props}
          />
          <CheckIcon
            className="pointer-events-none absolute h-3 w-3 text-white opacity-0 peer-checked:opacity-100"
            aria-hidden="true"
          />
        </span>
        <span className="text-secondary text-ink-secondary">{label}</span>
      </label>
    );
  }
);

Checkbox.displayName = "Checkbox";
