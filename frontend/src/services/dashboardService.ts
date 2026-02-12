import api from '@/lib/axios';
import type {
  DashboardSummary,
  TimeseriesResponse,
  AgentUsageResponse,
  DashboardQueryParams,
} from '@/types';

export const dashboardService = {
  getSummary: async (params?: DashboardQueryParams): Promise<DashboardSummary> => {
    const response = await api.get<DashboardSummary>('/dashboard/summary', {
      params,
    });
    return response.data;
  },

  getTimeseries: async (params?: DashboardQueryParams): Promise<TimeseriesResponse> => {
    const response = await api.get<TimeseriesResponse>('/dashboard/usage/timeseries', {
      params,
    });
    return response.data;
  },

  getByAgent: async (
    params?: Omit<DashboardQueryParams, 'agent_id'>
  ): Promise<AgentUsageResponse> => {
    const response = await api.get<AgentUsageResponse>('/dashboard/usage/by-agent', {
      params,
    });
    return response.data;
  },
};
