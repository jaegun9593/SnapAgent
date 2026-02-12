import { useState } from 'react';
import {
  ChevronDown,
  ChevronRight,
  Search,
  Globe,
  Plug,
  Loader2,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { ToolExecutionDetail } from './ToolExecutionDetail';
import type { ToolExecution } from '@/types';

interface ToolExecutionLayerProps {
  executions: ToolExecution[];
  isCollapsible?: boolean;
}

const toolIcons: Record<string, React.ReactNode> = {
  rag: <Search className="h-3.5 w-3.5" />,
  web_search: <Globe className="h-3.5 w-3.5" />,
  custom_api: <Plug className="h-3.5 w-3.5" />,
};

const toolLabels: Record<string, string> = {
  rag: 'RAG 검색',
  web_search: '웹 검색',
  custom_api: 'API 호출',
};

export function ToolExecutionLayer({
  executions,
  isCollapsible = true,
}: ToolExecutionLayerProps) {
  const [isOpen, setIsOpen] = useState(true);

  const completedCount = executions.filter(
    (e) => e.status === 'completed'
  ).length;
  const runningCount = executions.filter((e) => e.status === 'running').length;
  const errorCount = executions.filter((e) => e.status === 'error').length;
  const allDone = runningCount === 0;

  const summaryText = allDone
    ? `${completedCount}개 도구 실행 완료${errorCount > 0 ? ` (${errorCount}개 오류)` : ''}`
    : `${runningCount}개 도구 실행 중...`;

  const content = (
    <div className="space-y-2">
      {executions.map((execution, idx) => (
        <ToolExecutionDetail key={idx} execution={execution} />
      ))}
    </div>
  );

  if (!isCollapsible) {
    return (
      <div className="rounded-md border bg-muted/30 p-3 space-y-2">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          {allDone ? (
            <CheckCircle2 className="h-4 w-4 text-green-500" />
          ) : (
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
          )}
          <span className="font-medium">{summaryText}</span>
        </div>
        {content}
      </div>
    );
  }

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <div className="rounded-md border bg-muted/30 overflow-hidden">
        <CollapsibleTrigger asChild>
          <button
            className={cn(
              'flex items-center gap-2 w-full px-3 py-2 text-sm transition-colors hover:bg-muted/50',
              'text-left'
            )}
          >
            {isOpen ? (
              <ChevronDown className="h-4 w-4 shrink-0" />
            ) : (
              <ChevronRight className="h-4 w-4 shrink-0" />
            )}

            {allDone ? (
              <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
            ) : (
              <Loader2 className="h-4 w-4 animate-spin text-primary shrink-0" />
            )}

            <span className="font-medium text-muted-foreground flex-1">
              {summaryText}
            </span>

            <div className="flex items-center gap-1">
              {executions.map((exec, idx) => (
                <Badge
                  key={idx}
                  variant={
                    exec.status === 'completed'
                      ? 'secondary'
                      : exec.status === 'error'
                        ? 'destructive'
                        : 'outline'
                  }
                  className="text-xs px-1.5 py-0"
                >
                  <span className="flex items-center gap-1">
                    {toolIcons[exec.tool_type] || <Plug className="h-3 w-3" />}
                    {toolLabels[exec.tool_type] || exec.tool_type}
                  </span>
                </Badge>
              ))}
            </div>
          </button>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <div className="px-3 pb-3 pt-1 border-t border-border/50">
            {content}
          </div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
}
