import api from '@/lib/axios';
import type {
  ChatSession,
  ChatSessionCreate,
  ChatSessionListResponse,
  ChatMessage,
  ChatMessageCreate,
  ChatMessageListResponse,
  StreamEvent,
} from '@/types';

export const chatService = {
  // Session CRUD
  async listSessions(agentId?: string): Promise<ChatSessionListResponse> {
    const params = agentId ? { agent_id: agentId } : {};
    const response = await api.get<ChatSessionListResponse>('/chat/sessions', { params });
    return response.data;
  },

  async createSession(data: ChatSessionCreate): Promise<ChatSession> {
    const response = await api.post<ChatSession>('/chat/sessions', data);
    return response.data;
  },

  async getSession(sessionId: string): Promise<ChatSession> {
    const response = await api.get<ChatSession>(`/chat/sessions/${sessionId}`);
    return response.data;
  },

  async deleteSession(sessionId: string): Promise<void> {
    await api.delete(`/chat/sessions/${sessionId}`);
  },

  // Message CRUD
  async getMessages(sessionId: string): Promise<ChatMessageListResponse> {
    const response = await api.get<ChatMessageListResponse>(
      `/chat/sessions/${sessionId}/messages`
    );
    return response.data;
  },

  // SSE streaming message
  async sendMessageStream(
    sessionId: string,
    data: ChatMessageCreate,
    onEvent: (event: StreamEvent) => void,
    onError?: (error: Error) => void
  ): Promise<void> {
    const token = localStorage.getItem('access_token');
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    const url = `${baseUrl}/chat/sessions/${sessionId}/messages`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6).trim();
            if (jsonStr === '[DONE]') continue;
            try {
              const event: StreamEvent = JSON.parse(jsonStr);
              onEvent(event);
            } catch {
              // Skip malformed JSON
            }
          }
        }
      }

      // Process remaining buffer
      if (buffer.startsWith('data: ')) {
        const jsonStr = buffer.slice(6).trim();
        if (jsonStr && jsonStr !== '[DONE]') {
          try {
            const event: StreamEvent = JSON.parse(jsonStr);
            onEvent(event);
          } catch {
            // Skip malformed JSON
          }
        }
      }
    } catch (error) {
      if (onError) {
        onError(error instanceof Error ? error : new Error(String(error)));
      }
    }
  },
};
