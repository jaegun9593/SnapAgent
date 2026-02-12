import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { agentService } from '@/services/agentService';
import type {
  AgentCreate,
  AgentUpdate,
  AgentTestRequest,
  AgentProcessRequest,
} from '@/types';

export function useAgents() {
  const queryClient = useQueryClient();

  const {
    data: agentsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['agents'],
    queryFn: agentService.list,
  });

  const createMutation = useMutation({
    mutationFn: (data: AgentCreate) => agentService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: AgentUpdate }) =>
      agentService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => agentService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });

  const processMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data?: AgentProcessRequest }) =>
      agentService.process(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });

  return {
    agents: agentsData?.agents || [],
    total: agentsData?.total || 0,
    isLoading,
    error,
    createAgent: createMutation.mutate,
    createAgentAsync: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    updateAgent: updateMutation.mutate,
    updateAgentAsync: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    deleteAgent: deleteMutation.mutate,
    deleteAgentAsync: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
    processAgent: processMutation.mutate,
    processAgentAsync: processMutation.mutateAsync,
    isProcessing: processMutation.isPending,
  };
}

export function useAgent(agentId: string) {
  return useQuery({
    queryKey: ['agents', agentId],
    queryFn: () => agentService.get(agentId),
    enabled: !!agentId,
  });
}

export function useAgentStatus(agentId: string) {
  return useQuery({
    queryKey: ['agents', agentId, 'status'],
    queryFn: () => agentService.getStatus(agentId),
    enabled: !!agentId,
    refetchInterval: 5000, // Poll every 5 seconds
  });
}

export function useAgentTest() {
  return useMutation({
    mutationFn: ({ agentId, data }: { agentId: string; data: AgentTestRequest }) =>
      agentService.test(agentId, data),
  });
}
