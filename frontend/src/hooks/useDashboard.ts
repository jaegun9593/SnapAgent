import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '@/services/dashboardService';
import type { DashboardQueryParams } from '@/types';

export function useDashboardSummary(params?: DashboardQueryParams) {
  return useQuery({
    queryKey: ['dashboard', 'summary', params],
    queryFn: () => dashboardService.getSummary(params),
  });
}

export function useDashboardTimeseries(params?: DashboardQueryParams) {
  return useQuery({
    queryKey: ['dashboard', 'timeseries', params],
    queryFn: () => dashboardService.getTimeseries(params),
  });
}

export function useDashboardByAgent(params?: Omit<DashboardQueryParams, 'agent_id'>) {
  return useQuery({
    queryKey: ['dashboard', 'by-agent', params],
    queryFn: () => dashboardService.getByAgent(params),
  });
}
