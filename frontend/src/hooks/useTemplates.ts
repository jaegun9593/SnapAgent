import { useQuery } from '@tanstack/react-query';
import { templateService } from '@/services/templateService';

export function useTemplates(category?: string) {
  const {
    data: templatesData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['templates', category],
    queryFn: () => templateService.list(category),
  });

  return {
    templates: templatesData?.templates || [],
    total: templatesData?.total || 0,
    isLoading,
    error,
  };
}

export function useTemplate(templateId: string) {
  return useQuery({
    queryKey: ['templates', templateId],
    queryFn: () => templateService.get(templateId),
    enabled: !!templateId,
  });
}
