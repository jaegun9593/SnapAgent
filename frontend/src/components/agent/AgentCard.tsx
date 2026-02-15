import { MessageSquare, Pencil, Trash2, Clock, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Agent } from '@/types';

interface AgentCardProps {
  agent: Agent;
  onChat: () => void;
  onEdit: () => void;
  onDelete: () => void;
  isDeleting: boolean;
}

const statusConfig: Record<string, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
  draft: { label: '초안', variant: 'secondary' },
  configured: { label: '구성 완료', variant: 'outline' },
  processing: { label: '처리 중', variant: 'secondary' },
  ready: { label: '사용 가능', variant: 'default' },
  error: { label: '오류', variant: 'destructive' },
};

export function AgentCard({ agent, onChat, onEdit, onDelete, isDeleting }: AgentCardProps) {
  const status = statusConfig[agent.status] || statusConfig.draft;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">{agent.name}</CardTitle>
          </div>
          <Badge variant={status.variant}>{status.label}</Badge>
        </div>
        <CardDescription className="line-clamp-2">
          {agent.description || '설명 없음'}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-1">
        <div className="space-y-2 text-sm text-muted-foreground">
          {agent.tools && agent.tools.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {agent.tools.map((tool, idx) => (
                <Badge key={idx} variant="outline" className="text-xs">
                  {tool.tool_type === 'rag'
                    ? 'RAG'
                    : tool.tool_type === 'web_search'
                      ? '웹 검색'
                      : 'API'}
                </Badge>
              ))}
            </div>
          )}
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            <span>{formatDate(agent.updated_at)}</span>
          </div>
        </div>
      </CardContent>
      <CardFooter className="gap-2">
        <Button className="flex-1" onClick={onChat}>
          <MessageSquare className="mr-2 h-4 w-4" />
          채팅
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={onEdit}
        >
          <Pencil className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={onDelete}
          disabled={isDeleting}
        >
          <Trash2 className="h-4 w-4 text-destructive" />
        </Button>
      </CardFooter>
    </Card>
  );
}
