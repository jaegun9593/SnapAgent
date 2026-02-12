import api from '@/lib/axios';
import type {
  Template,
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
};
