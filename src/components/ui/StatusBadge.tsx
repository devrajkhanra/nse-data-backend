import React from 'react';
import { cn } from '../../utils/cn';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const getStatusColor = (status: string) => {
    const lowerStatus = status.toLowerCase();
    if (lowerStatus.includes('completed') || lowerStatus.includes('success')) {
      return 'bg-success-100 text-success-800 border-success-200';
    }
    if (lowerStatus.includes('error') || lowerStatus.includes('failed')) {
      return 'bg-error-100 text-error-800 border-error-200';
    }
    if (lowerStatus.includes('processing') || lowerStatus.includes('downloading')) {
      return 'bg-primary-100 text-primary-800 border-primary-200';
    }
    if (lowerStatus.includes('starting')) {
      return 'bg-warning-100 text-warning-800 border-warning-200';
    }
    return 'bg-slate-100 text-slate-800 border-slate-200';
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border',
        getStatusColor(status),
        className
      )}
    >
      {status}
    </span>
  );
};