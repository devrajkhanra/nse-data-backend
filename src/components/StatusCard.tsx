import React from 'react';
import { Database, Calendar, CheckCircle, AlertCircle } from 'lucide-react';
import { Card } from './ui/Card';
import { StatusBadge } from './ui/StatusBadge';
import { formatDisplayDate } from '../utils/date';

interface StatusCardProps {
  lastDownloadDate: string;
  isLoading?: boolean;
}

export const StatusCard: React.FC<StatusCardProps> = ({ 
  lastDownloadDate, 
  isLoading = false 
}) => {
  const hasData = lastDownloadDate && lastDownloadDate !== 'No data found';

  return (
    <Card variant="glass" className="p-6">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          <div className={`p-3 rounded-lg ${hasData ? 'bg-success-100' : 'bg-slate-100'}`}>
            <Database className={`w-6 h-6 ${hasData ? 'text-success-600' : 'text-slate-600'}`} />
          </div>
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-slate-800 mb-2">
            System Status
          </h3>
          
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              {hasData ? (
                <CheckCircle className="w-4 h-4 text-success-500" />
              ) : (
                <AlertCircle className="w-4 h-4 text-slate-400" />
              )}
              <span className="text-sm text-slate-600">
                Data folders initialized
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-slate-400" />
                <span className="text-sm text-slate-600">
                  Last download:
                </span>
              </div>
              {isLoading ? (
                <div className="animate-pulse bg-slate-200 h-4 w-24 rounded"></div>
              ) : (
                <StatusBadge 
                  status={hasData ? formatDisplayDate(lastDownloadDate) : 'No data'} 
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};