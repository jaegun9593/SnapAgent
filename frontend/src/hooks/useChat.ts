import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { chatService } from '@/services/chatService';
import type {
  ChatSessionCreate,
  ChatMessageCreate,
  StreamEvent,
  ToolExecution,
  ReActStep,
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
  const [reactSteps, setReactSteps] = useState<ReActStep[]>([]);
  const [toolExecutions, setToolExecutions] = useState<ToolExecution[]>([]);
  const [streamError, setStreamError] = useState<string | null>(null);

  const resetStream = useCallback(() => {
    setStreamContent('');
    setReactSteps([]);
    setToolExecutions([]);
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
            setReactSteps((prev) => [
              ...prev,
              {
                type: 'intent',
                status: 'completed',
                data: {
                  content: event.content,
                  intent: event.intent || 'unknown',
                  confidence: event.confidence || 0,
                  iteration: event.iteration || 1,
                },
                timestamp: new Date().toISOString(),
              },
            ]);
            break;
          case 'tool_start': {
            const toolExec: ToolExecution = {
              tool_type: event.tool_type,
              tool_name: event.tool_name,
              input: event.input,
              status: 'running',
              started_at: new Date().toISOString(),
            };
            setToolExecutions((prev) => [...prev, toolExec]);
            setReactSteps((prev) => [
              ...prev,
              {
                type: 'tool',
                status: 'running',
                data: {
                  tool_type: event.tool_type,
                  tool_name: event.tool_name,
                  input: event.input,
                },
                timestamp: new Date().toISOString(),
              },
            ]);
            break;
          }
          case 'tool_result': {
            // Safely extract string output (backend may send object or string)
            const toolOutput = typeof event.output === 'string'
              ? event.output
              : typeof event.output === 'object' && event.output !== null
                ? ((event.output as Record<string, unknown>).output as string || JSON.stringify(event.output))
                : String(event.output || '');

            setToolExecutions((prev) =>
              prev.map((t) =>
                t.tool_name === event.tool_name && t.status === 'running'
                  ? {
                      ...t,
                      output: toolOutput,
                      status: 'completed' as const,
                      completed_at: new Date().toISOString(),
                      duration_ms: event.duration_ms,
                    }
                  : t
              )
            );
            setReactSteps((prev) =>
              prev.map((s) =>
                s.type === 'tool' &&
                s.status === 'running' &&
                s.data.tool_name === event.tool_name
                  ? {
                      ...s,
                      status: 'completed',
                      data: {
                        ...s.data,
                        output: toolOutput,
                        duration_ms: event.duration_ms,
                      },
                    }
                  : s
              )
            );
            break;
          }
          case 'evaluation':
            setReactSteps((prev) => [
              ...prev,
              {
                type: 'evaluation',
                status: event.needs_retry ? 'running' : 'completed',
                data: {
                  score: event.score,
                  reasoning: event.reasoning,
                  needs_retry: event.needs_retry,
                },
                timestamp: new Date().toISOString(),
              },
            ]);
            break;
          case 'answer_token':
            setStreamContent((prev) => prev + event.content);
            break;
          case 'answer_end':
            break;
          case 'done':
            setIsStreaming(false);
            setStreamContent('');
            queryClient.invalidateQueries({
              queryKey: ['chat-messages', sessionId],
            });
            queryClient.invalidateQueries({
              queryKey: ['chat-sessions'],
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

      // Safety: ensure streaming state is reset when connection closes
      setIsStreaming(false);
    },
    [sessionId, queryClient, resetStream]
  );

  return {
    isStreaming,
    streamContent,
    reactSteps,
    toolExecutions,
    streamError,
    sendMessage,
    resetStream,
  };
}
