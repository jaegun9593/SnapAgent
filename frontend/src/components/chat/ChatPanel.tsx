import { useState, useEffect, useRef } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useChatSessions, useChatMessages, useStreamChat } from '@/hooks/useChat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { ToolExecutionLayer } from './ToolExecutionLayer';
import type { ChatMessage as ChatMessageType } from '@/types';

interface ChatPanelProps {
  agentId: string;
}

export function ChatPanel({ agentId }: ChatPanelProps) {
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const {
    sessions,
    createSessionAsync,
    isCreating: isCreatingSession,
  } = useChatSessions(agentId);

  const { messages } = useChatMessages(activeSessionId || '');

  const {
    isStreaming,
    streamContent,
    thinkingContent,
    toolExecutions,
    evaluation,
    streamError,
    sendMessage,
    resetStream,
  } = useStreamChat(activeSessionId || '');

  // Auto-select first session or create new one
  useEffect(() => {
    if (sessions.length > 0 && !activeSessionId) {
      setActiveSessionId(sessions[0].id);
    }
  }, [sessions, activeSessionId]);

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamContent, toolExecutions]);

  const handleNewSession = async () => {
    try {
      const session = await createSessionAsync({
        agent_id: agentId,
      });
      setActiveSessionId(session.id);
      resetStream();
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!activeSessionId) {
      // Create session first
      try {
        const session = await createSessionAsync({
          agent_id: agentId,
        });
        setActiveSessionId(session.id);
        // Wait a tick then send
        setTimeout(() => {
          sendMessage({ content });
        }, 100);
      } catch (err) {
        console.error('Failed to create session:', err);
      }
    } else {
      sendMessage({ content });
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Session tabs */}
      <div className="flex items-center gap-2 pb-3 border-b overflow-x-auto">
        {sessions.map((session) => (
          <Button
            key={session.id}
            variant={activeSessionId === session.id ? 'default' : 'outline'}
            size="sm"
            onClick={() => {
              setActiveSessionId(session.id);
              resetStream();
            }}
          >
            {session.title || '새 대화'}
          </Button>
        ))}
        <Button
          variant="ghost"
          size="sm"
          onClick={handleNewSession}
          disabled={isCreatingSession}
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 py-4">
        <div className="space-y-4 pr-4">
          {messages.map((msg: ChatMessageType) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}

          {/* Streaming state */}
          {isStreaming && (
            <div className="space-y-3">
              {/* Thinking indicator */}
              {thinkingContent && (
                <div className="text-sm text-muted-foreground italic px-4 py-2 bg-muted/30 rounded-md">
                  {thinkingContent}
                </div>
              )}

              {/* Tool executions */}
              {toolExecutions.length > 0 && (
                <ToolExecutionLayer
                  executions={toolExecutions}
                  isCollapsible={true}
                />
              )}

              {/* Evaluation result */}
              {evaluation && (
                <div className="text-xs text-muted-foreground px-4 py-1">
                  품질 점수: {(evaluation.score * 100).toFixed(0)}%
                  {evaluation.needs_retry && ' - 재시도 중...'}
                </div>
              )}

              {/* Streaming answer */}
              {streamContent && (
                <ChatMessage
                  message={{
                    id: 'streaming',
                    session_id: activeSessionId || '',
                    role: 'assistant',
                    content: streamContent,
                    created_at: new Date().toISOString(),
                  }}
                  isStreaming={true}
                />
              )}
            </div>
          )}

          {/* Stream error */}
          {streamError && (
            <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              오류: {streamError}
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="pt-4 border-t">
        <ChatInput
          onSend={handleSendMessage}
          disabled={isStreaming}
          placeholder="메시지를 입력하세요..."
        />
      </div>
    </div>
  );
}
