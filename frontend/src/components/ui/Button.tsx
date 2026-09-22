import { ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger";
  size?: "sm" | "default" | "lg";
  isLoading?: boolean;
}

/**
 * Base button used across the whole product, not just auth. Elevation on
 * hover is restricted to a 1px translate + soft shadow — no scale, no color
 * pulse — to stay inside "subtle professional animation" territory.
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    { variant = "primary", size = "default", isLoading = false, disabled, className = "", children, ...props },
    ref
  ) => {
    const base =
      "inline-flex items-center justify-center gap-2 rounded-btn " +
      "text-body font-semibold transition-all duration-150 ease-out " +
      "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 " +
      "disabled:cursor-not-allowed disabled:opacity-60";

    const variants: Record<NonNullable<ButtonProps["variant"]>, string> = {
      primary:
        "bg-primary text-white shadow-card hover:bg-primary-hover hover:shadow-raised focus-visible:outline-primary",
      secondary:
        "border border-border bg-surface text-primary hover:border-border-strong hover:shadow-card focus-visible:outline-primary",
      danger:
        "bg-danger text-white shadow-card hover:brightness-95 hover:shadow-raised focus-visible:outline-danger",
    };
    const sizes = { sm: 'min-h-8 px-3 py-1.5 text-xs', default: 'min-h-11 px-4 py-2.5 text-body', lg: 'min-h-12 px-5 py-3 text-base' };

    return (
      <button
        ref={ref}
        className={`${base} ${sizes[size]} ${variants[variant]} ${className}`}
        disabled={disabled || isLoading}
        aria-busy={isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <span
              className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"
              aria-hidden="true"
            />
            <span>Loading…</span>
          </>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = "Button";
