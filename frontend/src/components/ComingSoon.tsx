import React from 'react';
import { ClockIcon } from '@heroicons/react/24/outline';

const ComingSoon: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-64 text-center">
      <ClockIcon className="w-16 h-16 text-secondary-300 mb-4" />
      <h2 className="text-lg font-medium text-secondary-700">Coming Soon</h2>
      <p className="text-sm text-secondary-500 max-w-sm">This feature is under active development. Check back later.</p>
    </div>
  );
};

export default ComingSoon;
