import { Link } from '@tanstack/react-router';
import { LockClosedIcon } from '@heroicons/react/24/outline';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/Button';

export function UpgradePrompt({ feature }: { feature: string }) {
  const title = feature.replace(/_/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
  return <Card className="mx-auto max-w-xl"><CardHeader><LockClosedIcon className="h-6 w-6 text-ink-secondary" /><CardTitle>{title} is not included in your current plan</CardTitle></CardHeader><CardContent><p className="mb-5 text-sm text-ink-secondary">Available on Professional and Enterprise plans.</p><Link to="/settings/subscription"><Button>See plans</Button></Link></CardContent></Card>;
}
