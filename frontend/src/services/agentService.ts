import api from '@/lib/axios';
import type {
  Agent,
  AgentCreate,
  AgentUpdate,
  AgentListResponse,
  AgentStatusResponse,
  AgentTestRequest,
  AgentTestResponse,
  AgentProcessRequest,
  AgentProcessResponse,
} from '@/types';

export const agentService = {
  async list(): Promise<AgentListResponse> {
    const response = await api.get<AgentListResponse>('/agents/');
    return response.data;
  },

  async get(agentId: string): Promise<Agent> {
    const response = await api.get<Agent>(`/agents/${agentId}`);
    return response.data;
  },

  async create(data: AgentCreate): Promise<Agent> {
    const response = await api.post<Agent>('/agents/', data);
    return response.data;
  },

  async update(agentId: string, data: AgentUpdate): Promise<Agent> {
    const response = await api.put<Agent>(`/agents/${agentId}`, data);
    return response.data;
  },

  async delete(agentId: string): Promise<void> {
    await api.delete(`/agents/${agentId}`);
  },

  async getStatus(agentId: string): Promise<AgentStatusResponse> {
    const response = await api.get<AgentStatusResponse>(`/agents/${agentId}/status`);
    return response.data;
  },

  async test(agentId: string, data: AgentTestRequest): Promise<AgentTestResponse> {
    const response = await api.post<AgentTestResponse>(`/agents/${agentId}/test`, data);
    return response.data;
  },

  async process(agentId: string, data?: AgentProcessRequest): Promise<AgentProcessResponse> {
    const response = await api.post<AgentProcessResponse>(
      `/agents/${agentId}/process`,
      data || {}
    );
    return response.data;
  },
};
