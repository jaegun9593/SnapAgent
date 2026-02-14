import { useState, useEffect, useRef } from 'react';
import { Plus, MessageSquare, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { useChatSessions, useChatMessages, useStreamChat } from '@/hooks/useChat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { LoadingIndicator } from './LoadingIndicator';
import { ToolExecutionLayer } from './ToolExecutionLayer';
import type { ChatMessage as ChatMessageType } from '@/types';

interface ChatPanelProps {
  agentId: string;
}

export function ChatPanel({ agentId }: ChatPanelProps) {
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);
  const [pendingUserMessage, setPendingUserMessage] = useState<ChatMessageType | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const {
    sessions,
    createSessionAsync,
    deleteSession,
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

  // Send pending message after session is created and hook has correct sessionId
  useEffect(() => {
    if (activeSessionId && pendingMessage) {
      // Optimistic UI: show user message immediately
      setPendingUserMessage({
        id: `pending-${Date.now()}`,
        session_id: activeSessionId,
        role: 'user',
        content: pendingMessage,
        created_at: new Date().toISOString(),
      });
      sendMessage({ content: pendingMessage });
      setPendingMessage(null);
    }
  }, [activeSessionId, pendingMessage, sendMessage]);

  // Clear pending user message once it appears in fetched messages
  useEffect(() => {
    if (pendingUserMessage && messages.length > 0) {
      const found = messages.some(
        (m) => m.role === 'user' && m.content === pendingUserMessage.content
      );
      if (found) {
        setPendingUserMessage(null);
      }
    }
  }, [messages, pendingUserMessage]);

  // Build display messages: fetched + pending user message
  const displayMessages = pendingUserMessage
    ? [...messages, pendingUserMessage]
    : messages;

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [displayMessages, streamContent, toolExecutions, isStreaming]);

  const handleNewSession = async () => {
    try {
      const session = await createSessionAsync({
        agent_id: agentId,
      });
      setActiveSessionId(session.id);
      resetStream();
      setPendingUserMessage(null);
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const handleDeleteSession = (sessionId: string) => {
    deleteSession(sessionId);
    if (activeSessionId === sessionId) {
      const remaining = sessions.filter((s) => s.id !== sessionId);
      setActiveSessionId(remaining.length > 0 ? remaining[0].id : null);
      resetStream();
      setPendingUserMessage(null);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!activeSessionId) {
      try {
        const session = await createSessionAsync({
          agent_id: agentId,
        });
        setActiveSessionId(session.id);
        setPendingMessage(content);
      } catch (err) {
        console.error('Failed to create session:', err);
      }
    } else {
      // Optimistic UI: show user message immediately
      setPendingUserMessage({
        id: `pending-${Date.now()}`,
        session_id: activeSessionId,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      });
      sendMessage({ content });
    }
  };

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    if (days === 0) {
      return d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
    }
    if (days === 1) return '어제';
    if (days < 7) return `${days}일 전`;
    return d.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="flex h-full rounded-lg border overflow-hidden">
      {/* Left: Session list */}
      <div className="w-60 shrink-0 border-r bg-muted/30 flex flex-col">
        <div className="p-3 border-b">
          <Button
            variant="outline"
            size="sm"
            className="w-full justify-start gap-2"
            onClick={handleNewSession}
            disabled={isCreatingSession}
          >
            <Plus className="h-4 w-4" />
            새 대화
          </Button>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            {sessions.length === 0 && (
              <div className="px-3 py-8 text-center text-xs text-muted-foreground">
                대화가 없습니다
              </div>
            )}
            {sessions.map((session) => (
              <div
                key={session.id}
                className={cn(
                  'group flex items-center gap-2 rounded-md px-3 py-2 text-sm cursor-pointer transition-colors',
                  activeSessionId === session.id
                    ? 'bg-background shadow-sm border'
                    : 'hover:bg-background/60'
                )}
                onClick={() => {
                  setActiveSessionId(session.id);
                  resetStream();
                  setPendingUserMessage(null);
                }}
              >
                <MessageSquare className="h-4 w-4 shrink-0 text-muted-foreground" />
                <div className="flex-1 min-w-0">
                  <div className="truncate font-medium">
                    {session.title || '새 대화'}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {formatDate(session.updated_at)}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 opacity-0 group-hover:opacity-100 shrink-0"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteSession(session.id);
                  }}
                >
                  <Trash2 className="h-3 w-3 text-muted-foreground" />
                </Button>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Right: Chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Messages */}
        <ScrollArea className="flex-1 px-4 py-4">
          <div className="space-y-4 max-w-3xl mx-auto">
            {displayMessages.length === 0 && !isStreaming && (
              <div className="flex items-center justify-center h-48 text-sm text-muted-foreground">
                메시지를 입력하여 대화를 시작하세요.
              </div>
            )}

            {displayMessages.map((msg: ChatMessageType) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}

            {/* Streaming state */}
            {isStreaming && (
              <div className="space-y-3">
                {toolExecutions.length > 0 && (
                  <ToolExecutionLayer
                    executions={toolExecutions}
                    isCollapsible={true}
                  />
                )}

                {streamContent ? (
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
                ) : (
                  <div className="flex gap-3">
                    <div className="h-8 w-8" />
                    <div className="flex items-center gap-2 rounded-lg bg-muted px-4 py-3">
                      <LoadingIndicator />
                      <span className="text-sm text-muted-foreground">생각 중...</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {streamError && (
              <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                오류: {streamError}
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        </ScrollArea>

        {/* Input */}
        <div className="px-4 py-3 border-t">
          <div className="max-w-3xl mx-auto">
            <ChatInput
              onSend={handleSendMessage}
              disabled={isStreaming}
              placeholder="메시지를 입력하세요..."
            />
          </div>
        </div>
      </div>
    </div>
  );
}
