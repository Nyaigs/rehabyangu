import type { ReactNode } from 'react';
import { usePlan } from '../hooks/usePlan';
import { SkeletonCard } from './Skeleton';
import { UpgradePrompt } from './UpgradePrompt';

export function FeatureGate({ feature, children }: { feature: string; children: ReactNode }) {
  const { features, isLoading } = usePlan();
  if (isLoading) return <SkeletonCard />;
  if (!features[feature]) return <UpgradePrompt feature={feature} />;
  return <>{children}</>;
}
