export interface FolderCheckResponse {
  lastDownloadDate: string;
}

export interface DownloadRequest {
  type: 'single' | 'range';
  dates: string | string[];
}

export interface DownloadResponse {
  status: string;
  successDates: string[];
  error?: string;
}

export interface ProgressResponse {
  current: number;
  total: number;
  status: string;
}

export interface ApiError {
  error: string;
}