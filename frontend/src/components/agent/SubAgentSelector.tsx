import { Check } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useAgents } from '@/hooks/useAgents';
import { cn } from '@/lib/utils';

interface SubAgentSelectorProps {
  selectedIds: string[];
  currentAgentId?: string;
  onChange: (ids: string[]) => void;
}

export function SubAgentSelector({
  selectedIds,
  currentAgentId,
  onChange,
}: SubAgentSelectorProps) {
  const { agents, isLoading } = useAgents();

  const availableAgents = agents.filter(
    (a) => a.id !== currentAgentId && a.status === 'ready'
  );

  const toggleAgent = (agentId: string) => {
    if (selectedIds.includes(agentId)) {
      onChange(selectedIds.filter((id) => id !== agentId));
    } else {
      onChange([...selectedIds, agentId]);
    }
  };

  if (isLoading) {
    return (
      <div className="text-sm text-muted-foreground">로딩 중...</div>
    );
  }

  if (availableAgents.length === 0) {
    return (
      <div className="text-sm text-muted-foreground">
        사용 가능한 서브 Agent가 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {availableAgents.map((agent) => {
        const isSelected = selectedIds.includes(agent.id);
        return (
          <button
            key={agent.id}
            type="button"
            className={cn(
              'flex items-center justify-between w-full p-3 rounded-md border text-left transition-colors',
              isSelected
                ? 'border-primary bg-primary/5'
                : 'border-border hover:border-primary/50'
            )}
            onClick={() => toggleAgent(agent.id)}
          >
            <div>
              <div className="font-medium text-sm">{agent.name}</div>
              {agent.description && (
                <div className="text-xs text-muted-foreground mt-0.5">
                  {agent.description}
                </div>
              )}
              <div className="flex gap-1 mt-1">
                {agent.tools?.map((t, i) => (
                  <Badge key={i} variant="outline" className="text-xs">
                    {t.tool_type}
                  </Badge>
                ))}
              </div>
            </div>
            {isSelected && <Check className="h-4 w-4 text-primary" />}
          </button>
        );
      })}
    </div>
  );
}
