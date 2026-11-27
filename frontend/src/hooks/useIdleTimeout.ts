import { useEffect, useRef } from 'react';

const WARN_MS = 9 * 60 * 1000;   // 9 min — show warning
const LOGOUT_MS = 10 * 60 * 1000; // 10 min — auto logout
const ACTIVITY_EVENTS = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'] as const;

interface Options {
  onWarn: () => void;
  onLogout: () => void;
  enabled?: boolean;
}

/**
 * Inactivity timeout per TRD 7.2.
 * - 9 min: call onWarn (show modal)
 * - 10 min: call onLogout
 * Any user activity resets both timers. Background tab (visibilitychange)
 * does not reset — clock keeps running, matching clinical-app expectations.
 */
export function useIdleTimeout({ onWarn, onLogout, enabled = true }: Options) {
  const warnTimer = useRef<number | null>(null);
  const logoutTimer = useRef<number | null>(null);

  useEffect(() => {
    if (!enabled) return;

    const clear = () => {
      if (warnTimer.current !== null) window.clearTimeout(warnTimer.current);
      if (logoutTimer.current !== null) window.clearTimeout(logoutTimer.current);
      warnTimer.current = null;
      logoutTimer.current = null;
    };

    const schedule = () => {
      clear();
      warnTimer.current = window.setTimeout(onWarn, WARN_MS);
      logoutTimer.current = window.setTimeout(onLogout, LOGOUT_MS);
    };

    const onActivity = () => schedule();
    ACTIVITY_EVENTS.forEach((ev) => window.addEventListener(ev, onActivity, { passive: true }));
    schedule();

    return () => {
      ACTIVITY_EVENTS.forEach((ev) => window.removeEventListener(ev, onActivity));
      clear();
    };
  }, [onWarn, onLogout, enabled]);
}
