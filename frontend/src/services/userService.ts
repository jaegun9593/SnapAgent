import api from '@/lib/axios';
import type { User, UserUpdate } from '@/types';

export const userService = {
  async getMe(): Promise<User> {
    const response = await api.get<User>('/users/me');
    return response.data;
  },

  async updateMe(data: UserUpdate): Promise<User> {
    const response = await api.put<User>('/users/me', data);
    return response.data;
  },

  async deleteMe(): Promise<void> {
    await api.delete('/users/me');
  },
};
