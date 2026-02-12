import { useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authService } from '@/services/authService';
import { useAuthStore } from '@/stores/authStore';
import type { LoginRequest, RegisterRequest } from '@/types';

export function useAuth() {
  const { setUser, setTokens, logout: logoutStore } = useAuthStore();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const queryClient = useQueryClient();

  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authService.register(data),
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });

  const logoutMutation = useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      logoutStore();
      queryClient.clear();
    },
  });

  const { data: user, isLoading } = useQuery({
    queryKey: ['user'],
    queryFn: () => authService.getMe(),
    enabled: isAuthenticated,
  });

  // Update user in store when fetched (via useEffect, not during render)
  useEffect(() => {
    if (user) {
      setUser(user);
    }
  }, [user, setUser]);

  return {
    user,
    isLoading,
    isAuthenticated,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout: logoutMutation.mutate,
    loginError: loginMutation.error,
    registerError: registerMutation.error,
    isLoginPending: loginMutation.isPending,
    isRegisterPending: registerMutation.isPending,
  };
}
