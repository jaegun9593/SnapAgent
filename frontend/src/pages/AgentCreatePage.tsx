import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { AgentCreateWizard } from '@/components/agent/AgentCreateWizard';

export function AgentCreatePage() {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/agents')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Agent 생성</h1>
          <p className="text-muted-foreground mt-1">
            단계별로 새로운 Agent를 구성합니다.
          </p>
        </div>
      </div>

      <AgentCreateWizard
        onComplete={(agentId) => navigate(`/agents/${agentId}/chat`)}
        onCancel={() => navigate('/agents')}
      />
    </div>
  );
}
