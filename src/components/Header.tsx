import React from 'react';
import { TrendingUp, Database } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-white/20 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-primary-600 rounded-lg">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">NSE Data Downloader</h1>
                <p className="text-sm text-slate-600">Professional Market Data Management</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-slate-600">
            <Database className="w-4 h-4" />
            <span>Connected to Flask Backend</span>
          </div>
        </div>
      </div>
    </header>
  );
};