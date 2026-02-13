import api from '@/lib/axios';
import type { FileItem, FileListResponse } from '@/types';

export const fileService = {
  async list(): Promise<FileListResponse> {
    const response = await api.get<FileListResponse>('/files/');
    return response.data;
  },

  async get(fileId: string): Promise<FileItem> {
    const response = await api.get<FileItem>(`/files/${fileId}`);
    return response.data;
  },

  async upload(files: File[]): Promise<FileItem[]> {
    const results: FileItem[] = [];
    for (const file of files) {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post<FileItem>('/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      results.push(response.data);
    }
    return results;
  },

  async delete(fileId: string): Promise<void> {
    await api.delete(`/files/${fileId}`);
  },

  getDownloadUrl(fileId: string): string {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    return `${baseUrl}/files/${fileId}/download`;
  },
};
