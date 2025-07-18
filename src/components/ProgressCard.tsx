import React from 'react';
import { Activity, Clock, CheckCircle2 } from 'lucide-react';
import { Card } from './ui/Card';
import { ProgressBar } from './ui/ProgressBar';
import { StatusBadge } from './ui/StatusBadge';
import { ProgressResponse } from '../types/api';

interface ProgressCardProps {
  progress: ProgressResponse;
  isVisible: boolean;
}

export const ProgressCard: React.FC<ProgressCardProps> = ({ progress, isVisible }) => {
  if (!isVisible) return null;

  const isCompleted = progress.current === progress.total && progress.total > 0;
  const isActive = progress.current < progress.total && progress.total > 0;

  return (
    <Card variant="glass" className="p-6 animate-slide-up">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${
              isCompleted ? 'bg-success-100' : 
              isActive ? 'bg-primary-100' : 'bg-slate-100'
            }`}>
              {isCompleted ? (
                <CheckCircle2 className="w-5 h-5 text-success-600" />
              ) : isActive ? (
                <Activity className="w-5 h-5 text-primary-600 animate-pulse" />
              ) : (
                <Clock className="w-5 h-5 text-slate-600" />
              )}
            </div>
            <h3 className="text-lg font-semibold text-slate-800">
              Download Progress
            </h3>
          </div>
          
          <StatusBadge status={progress.status} />
        </div>

        {progress.total > 0 && (
          <ProgressBar
            current={progress.current}
            total={progress.total}
            className="mt-4"
          />
        )}

        <div className="text-sm text-slate-600">
          {progress.total > 0 ? (
            <p>
              Processing NSE data files including indices, stocks, moving averages, and 5-minute data for Nifty 50 companies.
            </p>
          ) : (
            <p>Ready to start downloading NSE data.</p>
          )}
        </div>
      </div>
    </Card>
  );
};