import { useState, useRef, useEffect, useCallback } from 'react';
import { Loader2 } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { useAgentTest } from '@/hooks/useAgents';
import { ChatMessage } from '@/components/chat/ChatMessage';
import { ChatInput } from '@/components/chat/ChatInput';
import { ToolExecutionLayer } from '@/components/chat/ToolExecutionLayer';
import type { ChatMessage as ChatMessageType, ToolExecution } from '@/types';

interface TestStepProps {
  agentId: string;
}

interface TestMessage {
  message: ChatMessageType;
  toolExecutions?: ToolExecution[];
  tokenUsage?: Record<string, number>;
  latencyMs?: number;
  error?: string;
}

let msgIdCounter = 0;
function nextMsgId() {
  return `test-msg-${++msgIdCounter}`;
}

export function TestStep({ agentId }: TestStepProps) {
  const [messages, setMessages] = useState<TestMessage[]>([]);
  const [isPending, setIsPending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const testMutation = useAgentTest();

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isPending]);

  const handleSend = useCallback(
    async (content: string) => {
      if (isPending) return;

      // Add user message
      const userMsg: TestMessage = {
        message: {
          id: nextMsgId(),
          session_id: 'test',
          role: 'user',
          content,
          created_at: new Date().toISOString(),
        },
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsPending(true);

      try {
        const res = await testMutation.mutateAsync({
          agentId,
          data: { query: content },
        });

        // Build tool executions from response
        const toolExecutions: ToolExecution[] =
          res.tool_calls?.map((tc) => ({
            tool_type: (tc.tool as string) || (tc.tool_type as string) || 'unknown',
            tool_name: (tc.tool as string) || (tc.tool_name as string) || 'unknown',
            input: tc.input as Record<string, unknown>,
            output: (tc.output as string) || '',
            status: 'completed' as const,
            duration_ms: tc.duration_ms as number | undefined,
          })) || [];

        // Add assistant message
        const assistantMsg: TestMessage = {
          message: {
            id: nextMsgId(),
            session_id: 'test',
            role: 'assistant',
            content: res.response || '',
            token_usage: res.token_usage,
            created_at: new Date().toISOString(),
          },
          toolExecutions,
          tokenUsage: res.token_usage,
          latencyMs: res.latency_ms,
          error: res.error,
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch (err) {
        // Add error message
        const errorMsg: TestMessage = {
          message: {
            id: nextMsgId(),
            session_id: 'test',
            role: 'assistant',
            content: '',
            created_at: new Date().toISOString(),
          },
          error:
            err instanceof Error
              ? err.message
              : 'Agent 테스트 중 오류가 발생했습니다.',
        };
        setMessages((prev) => [...prev, errorMsg]);
      } finally {
        setIsPending(false);
      }
    },
    [agentId, isPending, testMutation]
  );

  return (
    <div className="flex flex-col h-[480px]">
      {/* Header */}
      <div className="pb-3 border-b mb-1">
        <h3 className="text-lg font-semibold">Agent 테스트</h3>
        <p className="text-sm text-muted-foreground">
          테스트 질문을 보내 Agent가 정상 동작하는지 확인합니다.
        </p>
      </div>

      {/* Messages area */}
      <ScrollArea className="flex-1 py-4">
        <div className="space-y-4 pr-4">
          {messages.length === 0 && !isPending && (
            <div className="flex items-center justify-center h-48 text-sm text-muted-foreground">
              테스트 질문을 입력해 보세요.
            </div>
          )}

          {messages.map((entry) => (
            <div key={entry.message.id} className="space-y-2">
              {/* Tool execution layer (before assistant message) */}
              {entry.message.role === 'assistant' &&
                entry.toolExecutions &&
                entry.toolExecutions.length > 0 && (
                  <ToolExecutionLayer
                    executions={entry.toolExecutions}
                    isCollapsible={true}
                  />
                )}

              {/* Error display */}
              {entry.message.role === 'assistant' && entry.error && (
                <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                  {entry.error}
                </div>
              )}

              {/* Message bubble (skip if empty assistant with error) */}
              {!(
                entry.message.role === 'assistant' &&
                !entry.message.content &&
                entry.error
              ) && <ChatMessage message={entry.message} />}

              {/* Latency badge */}
              {entry.message.role === 'assistant' && entry.latencyMs && (
                <div className="flex items-center gap-2 pl-11">
                  <Badge variant="outline" className="text-xs">
                    {entry.latencyMs}ms
                  </Badge>
                </div>
              )}
            </div>
          ))}

          {/* Loading indicator */}
          {isPending && (
            <div className="flex gap-3">
              <div className="h-8 w-8" />
              <div className="flex items-center gap-2 text-sm text-muted-foreground italic bg-muted/30 rounded-md px-4 py-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Agent가 응답을 생성하고 있습니다...
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="pt-3 border-t">
        <ChatInput
          onSend={handleSend}
          disabled={isPending}
          placeholder="테스트 질문을 입력하세요..."
        />
      </div>
    </div>
  );
}
