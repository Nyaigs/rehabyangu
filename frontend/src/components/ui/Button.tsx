import { ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
  isLoading?: boolean;
}

/**
 * Base button used across the whole product, not just auth. Elevation on
 * hover is restricted to a 1px translate + soft shadow — no scale, no color
 * pulse — to stay inside "subtle professional animation" territory.
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    { variant = "primary", isLoading = false, disabled, className = "", children, ...props },
    ref
  ) => {
    const base =
      "inline-flex w-full items-center justify-center gap-2 rounded-lg px-4 py-3 " +
      "text-body font-semibold transition-all duration-150 ease-out " +
      "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 " +
      "disabled:cursor-not-allowed disabled:opacity-60";

    const variants: Record<NonNullable<ButtonProps["variant"]>, string> = {
      primary:
        "bg-primary text-white shadow-card hover:-translate-y-[1px] hover:bg-primary-hover hover:shadow-raised focus-visible:outline-primary",
      secondary:
        "bg-surface text-primary border border-border hover:-translate-y-[1px] hover:border-border-strong hover:shadow-card focus-visible:outline-primary",
    };

    return (
      <button
        ref={ref}
        className={`${base} ${variants[variant]} ${className}`}
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
            <span>Signing in…</span>
          </>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = "Button";
