import axios from 'axios';
import { FolderCheckResponse, DownloadRequest, DownloadResponse, ProgressResponse } from '../types/api';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  async checkFolders(): Promise<FolderCheckResponse> {
    const response = await api.get<FolderCheckResponse>('/check-folders');
    return response.data;
  },

  async downloadData(request: DownloadRequest): Promise<DownloadResponse> {
    const response = await api.post<DownloadResponse>('/download-data', request);
    return response.data;
  },

  async getProgress(): Promise<ProgressResponse> {
    const response = await api.get<ProgressResponse>('/progress');
    return response.data;
  },
};

export default apiService;