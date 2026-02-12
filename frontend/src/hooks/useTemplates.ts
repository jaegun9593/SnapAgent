import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { templateService } from '@/services/templateService';
import type { TemplateCreate, TemplateUpdate } from '@/types';

export function useTemplates(category?: string) {
  const queryClient = useQueryClient();

  const {
    data: templatesData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['templates', category],
    queryFn: () => templateService.list(category),
  });

  const createMutation = useMutation({
    mutationFn: (data: TemplateCreate) => templateService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: TemplateUpdate }) =>
      templateService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => templateService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
    },
  });

  return {
    templates: templatesData?.templates || [],
    total: templatesData?.total || 0,
    isLoading,
    error,
    createTemplate: createMutation.mutate,
    createTemplateAsync: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    updateTemplate: updateMutation.mutate,
    updateTemplateAsync: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    deleteTemplate: deleteMutation.mutate,
    deleteTemplateAsync: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
  };
}

export function useTemplate(templateId: string) {
  return useQuery({
    queryKey: ['templates', templateId],
    queryFn: () => templateService.get(templateId),
    enabled: !!templateId,
  });
}
