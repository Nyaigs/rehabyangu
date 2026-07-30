import React from 'react';

interface SkeletonProps {
  className?: string;
  count?: number;
}

export const SkeletonCard: React.FC<SkeletonProps> = ({ className = '', count = 1 }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`animate-pulse bg-secondary-200 rounded-lg ${className}`}
          style={{ minHeight: '100px' }}
        />
      ))}
    </>
  );
};

export const SkeletonText: React.FC<{ className?: string; width?: string }> = ({ className = '', width = 'w-full' }) => (
  <div className={`animate-pulse bg-secondary-200 rounded h-3 ${width} ${className}`} />
);

export const SkeletonCircle: React.FC<{ size?: string; className?: string }> = ({ size = 'w-10 h-10', className = '' }) => (
  <div className={`animate-pulse bg-secondary-200 rounded-full ${size} ${className}`} />
);

export const SkeletonTable: React.FC<{ rows?: number; cols?: number }> = ({ rows = 5, cols = 4 }) => {
  return (
    <div className="animate-pulse space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-2">
          {Array.from({ length: cols }).map((_, j) => (
            <div key={j} className="h-6 bg-secondary-200 rounded flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
};

export const SkeletonPatientCard: React.FC<{ count?: number }> = ({ count = 3 }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="card p-4">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <SkeletonText width="w-3/4" className="mb-1" />
              <SkeletonText width="w-1/2" className="mb-2" />
              <SkeletonText width="w-1/3" />
            </div>
            <SkeletonCircle size="w-5 h-5" />
          </div>
        </div>
      ))}
    </div>
  );
};
