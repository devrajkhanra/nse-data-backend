import React from 'react';
import { cn } from '../../utils/cn';

interface ProgressBarProps {
  current: number;
  total: number;
  className?: string;
  showPercentage?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  current,
  total,
  className,
  showPercentage = true
}) => {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;

  return (
    <div className={cn('space-y-2', className)}>
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showPercentage && (
        <div className="flex justify-between text-sm text-slate-600">
          <span>{current} of {total} completed</span>
          <span>{percentage}%</span>
        </div>
      )}
    </div>
  );
};