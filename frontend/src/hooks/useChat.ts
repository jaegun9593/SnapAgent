import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { chatService } from '@/services/chatService';
import type {
  ChatSessionCreate,
  ChatMessageCreate,
  StreamEvent,
  ToolExecution,
} from '@/types';

export function useChatSessions(agentId?: string) {
  const queryClient = useQueryClient();

  const {
    data: sessionsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['chat-sessions', agentId],
    queryFn: () => chatService.listSessions(agentId),
  });

  const createMutation = useMutation({
    mutationFn: (data: ChatSessionCreate) => chatService.createSession(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => chatService.deleteSession(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chat-sessions'] });
    },
  });

  return {
    sessions: sessionsData?.sessions || [],
    total: sessionsData?.total || 0,
    isLoading,
    error,
    createSession: createMutation.mutate,
    createSessionAsync: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    deleteSession: deleteMutation.mutate,
    isDeleting: deleteMutation.isPending,
  };
}

export function useChatMessages(sessionId: string) {
  const {
    data: messagesData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['chat-messages', sessionId],
    queryFn: () => chatService.getMessages(sessionId),
    enabled: !!sessionId,
  });

  return {
    messages: messagesData?.messages || [],
    total: messagesData?.total || 0,
    isLoading,
    error,
    refetch,
  };
}

export function useStreamChat(sessionId: string) {
  const queryClient = useQueryClient();
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamContent, setStreamContent] = useState('');
  const [thinkingContent, setThinkingContent] = useState('');
  const [toolExecutions, setToolExecutions] = useState<ToolExecution[]>([]);
  const [evaluation, setEvaluation] = useState<{
    score: number;
    reasoning: string;
    needs_retry: boolean;
  } | null>(null);
  const [streamError, setStreamError] = useState<string | null>(null);

  const resetStream = useCallback(() => {
    setStreamContent('');
    setThinkingContent('');
    setToolExecutions([]);
    setEvaluation(null);
    setStreamError(null);
  }, []);

  const sendMessage = useCallback(
    async (data: ChatMessageCreate) => {
      if (!sessionId) return;

      setIsStreaming(true);
      resetStream();

      const handleEvent = (event: StreamEvent) => {
        switch (event.type) {
          case 'thinking':
            setThinkingContent((prev) => prev + event.content);
            break;
          case 'tool_start':
            setToolExecutions((prev) => [
              ...prev,
              {
                tool_type: event.tool_type,
                tool_name: event.tool_name,
                input: event.input,
                status: 'running',
                started_at: new Date().toISOString(),
              },
            ]);
            break;
          case 'tool_result':
            setToolExecutions((prev) =>
              prev.map((t) =>
                t.tool_name === event.tool_name && t.status === 'running'
                  ? {
                      ...t,
                      output: event.output,
                      status: 'completed' as const,
                      completed_at: new Date().toISOString(),
                      duration_ms: event.duration_ms,
                    }
                  : t
              )
            );
            break;
          case 'evaluation':
            setEvaluation({
              score: event.score,
              reasoning: event.reasoning,
              needs_retry: event.needs_retry,
            });
            break;
          case 'answer_token':
            setStreamContent((prev) => prev + event.content);
            break;
          case 'answer_end':
          case 'done':
            setIsStreaming(false);
            queryClient.invalidateQueries({
              queryKey: ['chat-messages', sessionId],
            });
            break;
          case 'error':
            setStreamError(event.error);
            setIsStreaming(false);
            break;
        }
      };

      const handleError = (error: Error) => {
        setStreamError(error.message);
        setIsStreaming(false);
      };

      await chatService.sendMessageStream(
        sessionId,
        data,
        handleEvent,
        handleError
      );
    },
    [sessionId, queryClient, resetStream]
  );

  return {
    isStreaming,
    streamContent,
    thinkingContent,
    toolExecutions,
    evaluation,
    streamError,
    sendMessage,
    resetStream,
  };
}
