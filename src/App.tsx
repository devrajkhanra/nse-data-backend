import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { StatusCard } from './components/StatusCard';
import { DateSelector } from './components/DateSelector';
import { ProgressCard } from './components/ProgressCard';
import { apiService } from './services/api';
import { useProgress } from './hooks/useProgress';
import { AlertCircle, Wifi, WifiOff } from 'lucide-react';

function App() {
  const [lastDownloadDate, setLastDownloadDate] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string>('');
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const { progress } = useProgress(isDownloading);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    checkFolders();
  }, []);

  const checkFolders = async () => {
    try {
      setIsLoading(true);
      setError('');
      const response = await apiService.checkFolders();
      setLastDownloadDate(response.lastDownloadDate);
    } catch (err) {
      setError('Failed to connect to backend. Please ensure the Flask server is running on port 5000.');
      console.error('Error checking folders:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDateSelect = async (type: 'single' | 'range', dates: string | string[]) => {
    try {
      setIsDownloading(true);
      setError('');
      
      const response = await apiService.downloadData({ type, dates });
      
      if (response.status === 'completed') {
        // Refresh the status after completion
        await checkFolders();
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to download data. Please try again.');
      console.error('Error downloading data:', err);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Connection Status */}
          <div className="mb-6">
            <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${
              isOnline 
                ? 'bg-success-100 text-success-800' 
                : 'bg-error-100 text-error-800'
            }`}>
              {isOnline ? (
                <Wifi className="w-4 h-4" />
              ) : (
                <WifiOff className="w-4 h-4" />
              )}
              <span>{isOnline ? 'Online' : 'Offline'}</span>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-6 p-4 bg-error-50 border border-error-200 rounded-lg animate-fade-in">
              <div className="flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-error-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-sm font-medium text-error-800">Error</h3>
                  <p className="text-sm text-error-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column */}
            <div className="space-y-6">
              <StatusCard 
                lastDownloadDate={lastDownloadDate} 
                isLoading={isLoading}
              />
              
              <DateSelector 
                onDateSelect={handleDateSelect}
                disabled={isDownloading || !isOnline}
              />
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              <ProgressCard 
                progress={progress}
                isVisible={isDownloading || progress.total > 0}
              />

              {/* Info Card */}
              <div className="bg-gradient-to-br from-primary-50 to-blue-50 rounded-xl p-6 border border-primary-100">
                <h3 className="text-lg font-semibold text-primary-800 mb-3">
                  What gets downloaded?
                </h3>
                <ul className="space-y-2 text-sm text-primary-700">
                  <li className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                    <span>NSE Indices data (Nifty, Sensex, etc.)</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                    <span>Complete stock market data (Bhav Copy)</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                    <span>Moving averages data</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-primary-500 rounded-full"></div>
                    <span>5-minute data for Nifty 50 stocks</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;