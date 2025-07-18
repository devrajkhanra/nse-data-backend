import React from 'react';
import { Github, ExternalLink } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white/50 backdrop-blur-sm border-t border-white/20 mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="text-sm text-slate-600">
            <p>© 2025 NSE Data Downloader. Built with React & Flask.</p>
          </div>
          
          <div className="flex items-center space-x-6">
            <a
              href="https://www.nseindia.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1 text-sm text-slate-600 hover:text-primary-600 transition-colors"
            >
              <ExternalLink className="w-4 h-4" />
              <span>NSE India</span>
            </a>
            <a
              href="#"
              className="flex items-center space-x-1 text-sm text-slate-600 hover:text-primary-600 transition-colors"
            >
              <Github className="w-4 h-4" />
              <span>Source Code</span>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};