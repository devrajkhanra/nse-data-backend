import React from 'react';
import { cn } from '../../utils/cn';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'glass';
}

export const Card: React.FC<CardProps> = ({ 
  children, 
  className, 
  variant = 'default' 
}) => {
  return (
    <div
      className={cn(
        'rounded-xl shadow-lg border transition-all duration-200',
        variant === 'glass' 
          ? 'glass-card' 
          : 'bg-white border-slate-200 hover:shadow-xl',
        className
      )}
    >
      {children}
    </div>
  );
};