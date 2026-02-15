import { useNavigate } from 'react-router-dom';
import { Plus, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAgents } from '@/hooks/useAgents';
import { AgentCard } from '@/components/agent/AgentCard';

export function MyAgentsPage() {
  const navigate = useNavigate();
  const { agents, isLoading, deleteAgentAsync, isDeleting } = useAgents();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">내 Agent</h1>
          <p className="text-muted-foreground mt-1">
            생성한 Agent를 관리하고 채팅을 시작하세요.
          </p>
        </div>
        <Button onClick={() => navigate('/agents/create')}>
          <Plus className="mr-2 h-4 w-4" />
          Agent 생성
        </Button>
      </div>

      {agents.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-center">
          <Bot className="h-16 w-16 text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-semibold">아직 생성된 Agent가 없습니다</h3>
          <p className="text-muted-foreground mt-2 max-w-md">
            새로운 Agent를 생성하여 RAG 기반 대화를 시작해보세요.
            템플릿을 사용하면 더 빠르게 시작할 수 있습니다.
          </p>
          <Button className="mt-4" onClick={() => navigate('/agents/create')}>
            <Plus className="mr-2 h-4 w-4" />
            첫 Agent 만들기
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onChat={() => navigate(`/agents/${agent.id}/chat`)}
              onEdit={() => navigate(`/agents/${agent.id}/edit`)}
              onDelete={async () => {
                if (confirm('정말 이 Agent를 삭제하시겠습니까?')) {
                  await deleteAgentAsync(agent.id);
                }
              }}
              isDeleting={isDeleting}
            />
          ))}
        </div>
      )}
    </div>
  );
}
