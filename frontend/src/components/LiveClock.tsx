import { useEffect, useState } from 'react';

function formatNow(date: Date): string {
  const weekday = date.toLocaleDateString(undefined, { weekday: 'short' });
  const day = date.getDate();
  const month = date.toLocaleDateString(undefined, { month: 'short' });
  const year = date.getFullYear();
  const time = date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
  return `${weekday}, ${day} ${month} ${year} · ${time}`;
}

export function LiveClock() {
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(id);
  }, []);

  return (
    <span
      className="hidden items-center gap-1.5 text-sm font-medium text-slate-700 md:inline-flex"
      aria-label="Current date and time"
    >
      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" aria-hidden="true" />
      <time>{formatNow(now)}</time>
    </span>
  );
}
