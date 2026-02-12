import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAgent } from '@/hooks/useAgents';
import { ChatPanel } from '@/components/chat/ChatPanel';

export function AgentChatPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: agent, isLoading } = useAgent(id || '');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">로딩 중...</div>
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Agent를 찾을 수 없습니다.</div>
      </div>
    );
  }

  const statusVariant =
    agent.status === 'ready'
      ? 'default'
      : agent.status === 'error'
        ? 'destructive'
        : 'secondary';

  const statusLabel: Record<string, string> = {
    draft: '초안',
    configured: '구성 완료',
    processing: '처리 중',
    ready: '사용 가능',
    error: '오류',
  };

  return (
    <div className="flex flex-col h-[calc(100vh-7rem)]">
      <div className="flex items-center justify-between pb-4 border-b">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/agents')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold">{agent.name}</h1>
              <Badge variant={statusVariant}>
                {statusLabel[agent.status] || agent.status}
              </Badge>
            </div>
            {agent.description && (
              <p className="text-sm text-muted-foreground mt-0.5">
                {agent.description}
              </p>
            )}
          </div>
        </div>
        <Button variant="outline" size="sm">
          <Settings className="mr-2 h-4 w-4" />
          설정
        </Button>
      </div>

      <div className="flex-1 mt-4 overflow-hidden">
        <ChatPanel agentId={agent.id} />
      </div>
    </div>
  );
}
