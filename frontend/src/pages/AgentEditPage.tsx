import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAgent } from '@/hooks/useAgents';
import { AgentEditWizard } from '@/components/agent/AgentEditWizard';

export function AgentEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: agent, isLoading, error } = useAgent(id || '');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !agent) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <p className="text-destructive">Agent를 불러올 수 없습니다.</p>
        <Button variant="outline" className="mt-4" onClick={() => navigate('/agents')}>
          목록으로 돌아가기
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/agents')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Agent 수정</h1>
          <p className="text-muted-foreground mt-1">
            Agent의 설정을 수정합니다.
          </p>
        </div>
      </div>

      <AgentEditWizard
        agent={agent}
        onComplete={() => navigate(`/agents/${agent.id}/chat`)}
        onCancel={() => navigate('/agents')}
      />
    </div>
  );
}
