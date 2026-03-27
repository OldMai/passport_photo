/**
 * API client for the passport photo backend
 */

import axios from 'axios';
import type { UploadResponse, ProcessResponse } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadImage = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const processImage = async (uploadId: string): Promise<ProcessResponse> => {
  const response = await api.post<ProcessResponse>('/process', {
    upload_id: uploadId,
  });

  return response.data;
};

export const getDownloadUrl = (jobId: string, type: 'single' | 'print_layout'): string => {
  return `/api/download/${jobId}/${type}`;
};

export default api;
