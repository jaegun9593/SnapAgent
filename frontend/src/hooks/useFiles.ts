import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fileService } from '@/services/fileService';

export function useFiles() {
  const queryClient = useQueryClient();

  const {
    data: filesData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['files'],
    queryFn: fileService.list,
  });

  const uploadMutation = useMutation({
    mutationFn: (files: File[]) => fileService.upload(files),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => fileService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] });
    },
  });

  return {
    files: filesData?.files || [],
    total: filesData?.total || 0,
    isLoading,
    error,
    uploadFiles: uploadMutation.mutate,
    uploadFilesAsync: uploadMutation.mutateAsync,
    isUploading: uploadMutation.isPending,
    deleteFile: deleteMutation.mutate,
    deleteFileAsync: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
  };
}
