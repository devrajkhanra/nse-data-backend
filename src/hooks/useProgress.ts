import { useState, useEffect, useCallback } from 'react';
import { ProgressResponse } from '../types/api';
import { apiService } from '../services/api';

export const useProgress = (isDownloading: boolean) => {
  const [progress, setProgress] = useState<ProgressResponse>({
    current: 0,
    total: 0,
    status: 'Idle'
  });

  const fetchProgress = useCallback(async () => {
    try {
      const progressData = await apiService.getProgress();
      setProgress(progressData);
    } catch (error) {
      console.error('Error fetching progress:', error);
    }
  }, []);

  useEffect(() => {
    if (!isDownloading) return;

    const interval = setInterval(fetchProgress, 1000);
    return () => clearInterval(interval);
  }, [isDownloading, fetchProgress]);

  return { progress, fetchProgress };
};