import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;

  setUser: (user: User | null) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      setUser: (user) => set({ user, isAuthenticated: !!user }),

      setTokens: (accessToken, refreshToken) => {
        // Store tokens in localStorage for axios interceptor
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);

        set({
          accessToken,
          refreshToken,
          isAuthenticated: true,
        });
      },

      logout: () => {
        // Clear tokens from localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');

        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        // After rehydration, verify tokens exist in localStorage
        if (state?.isAuthenticated) {
          const token = localStorage.getItem('access_token');
          if (!token && state.accessToken) {
            // Restore tokens from Zustand persist to localStorage
            localStorage.setItem('access_token', state.accessToken);
            if (state.refreshToken) {
              localStorage.setItem('refresh_token', state.refreshToken);
            }
          } else if (!token && !state.accessToken) {
            // No tokens anywhere - force logout via setState (triggers re-renders)
            useAuthStore.setState({
              user: null,
              accessToken: null,
              refreshToken: null,
              isAuthenticated: false,
            });
          }
        }
      },
    }
  )
);
