import api from '@/lib/axios';
import type {
  Template,
  TemplateCreate,
  TemplateUpdate,
  TemplateListResponse,
} from '@/types';

export const templateService = {
  async list(category?: string): Promise<TemplateListResponse> {
    const params = category ? { category } : {};
    const response = await api.get<TemplateListResponse>('/templates/', { params });
    return response.data;
  },

  async get(templateId: string): Promise<Template> {
    const response = await api.get<Template>(`/templates/${templateId}`);
    return response.data;
  },

  async create(data: TemplateCreate): Promise<Template> {
    const response = await api.post<Template>('/templates/', data);
    return response.data;
  },

  async update(templateId: string, data: TemplateUpdate): Promise<Template> {
    const response = await api.put<Template>(`/templates/${templateId}`, data);
    return response.data;
  },

  async delete(templateId: string): Promise<void> {
    await api.delete(`/templates/${templateId}`);
  },
};
