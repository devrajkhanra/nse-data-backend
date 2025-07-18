import React, { useState } from 'react';
import { Calendar, CalendarRange } from 'lucide-react';
import { Card } from './ui/Card';
import { Button } from './ui/Button';
import { cn } from '../utils/cn';

interface DateSelectorProps {
  onDateSelect: (type: 'single' | 'range', dates: string | string[]) => void;
  disabled?: boolean;
}

export const DateSelector: React.FC<DateSelectorProps> = ({ onDateSelect, disabled }) => {
  const [dateType, setDateType] = useState<'single' | 'range'>('single');
  const [singleDate, setSingleDate] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (dateType === 'single') {
      if (!singleDate) return;
      onDateSelect('single', singleDate);
    } else {
      if (!startDate || !endDate) return;
      onDateSelect('range', [startDate, endDate]);
    }
  };

  const isFormValid = dateType === 'single' ? !!singleDate : !!(startDate && endDate);

  return (
    <Card variant="glass" className="p-6">
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Select Download Dates</h3>
          
          {/* Date Type Selector */}
          <div className="flex space-x-1 bg-slate-100 p-1 rounded-lg mb-6">
            <button
              type="button"
              onClick={() => setDateType('single')}
              className={cn(
                'flex-1 flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
                dateType === 'single'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-800'
              )}
            >
              <Calendar className="w-4 h-4 mr-2" />
              Single Date
            </button>
            <button
              type="button"
              onClick={() => setDateType('range')}
              className={cn(
                'flex-1 flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
                dateType === 'range'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-800'
              )}
            >
              <CalendarRange className="w-4 h-4 mr-2" />
              Date Range
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {dateType === 'single' ? (
            <div>
              <label htmlFor="single-date" className="block text-sm font-medium text-slate-700 mb-2">
                Select Date
              </label>
              <input
                id="single-date"
                type="date"
                value={singleDate}
                onChange={(e) => setSingleDate(e.target.value)}
                className="input-field"
                disabled={disabled}
              />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="start-date" className="block text-sm font-medium text-slate-700 mb-2">
                  Start Date
                </label>
                <input
                  id="start-date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="input-field"
                  disabled={disabled}
                />
              </div>
              <div>
                <label htmlFor="end-date" className="block text-sm font-medium text-slate-700 mb-2">
                  End Date
                </label>
                <input
                  id="end-date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  min={startDate}
                  className="input-field"
                  disabled={disabled}
                />
              </div>
            </div>
          )}

          <Button
            type="submit"
            disabled={!isFormValid || disabled}
            className="w-full"
          >
            Start Download
          </Button>
        </form>
      </div>
    </Card>
  );
};