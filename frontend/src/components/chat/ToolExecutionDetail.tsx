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
  Clock,
  Sparkles,
  BookOpen,
  GraduationCap,
  Calculator,
  Terminal,
  FileDown,
} from 'lucide-react';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { ToolExecution } from '@/types';

interface ToolExecutionDetailProps {
  execution: ToolExecution;
}

const toolIcons: Record<string, React.ReactNode> = {
  rag: <Search className="h-3.5 w-3.5" />,
  web_search: <Globe className="h-3.5 w-3.5" />,
  tavily_search: <Sparkles className="h-3.5 w-3.5" />,
  wikipedia: <BookOpen className="h-3.5 w-3.5" />,
  arxiv: <GraduationCap className="h-3.5 w-3.5" />,
  calculator: <Calculator className="h-3.5 w-3.5" />,
  python_repl: <Terminal className="h-3.5 w-3.5" />,
  web_scraper: <FileDown className="h-3.5 w-3.5" />,
  custom_api: <Plug className="h-3.5 w-3.5" />,
};

const toolLabels: Record<string, string> = {
  rag: 'RAG 검색',
  web_search: '웹 검색',
  tavily_search: 'Tavily 검색',
  wikipedia: 'Wikipedia',
  arxiv: 'ArXiv 논문',
  calculator: '계산기',
  python_repl: 'Python 실행',
  web_scraper: '웹 스크래핑',
  custom_api: 'API 호출',
};

export function ToolExecutionDetail({ execution }: ToolExecutionDetailProps) {
  const [isOpen, setIsOpen] = useState(false);

  const icon = toolIcons[execution.tool_type] || <Plug className="h-3.5 w-3.5" />;
  const label = toolLabels[execution.tool_type] || execution.tool_name;

  const statusIcon =
    execution.status === 'completed' ? (
      <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
    ) : execution.status === 'error' ? (
      <AlertCircle className="h-3.5 w-3.5 text-destructive" />
    ) : (
      <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
    );

  const hasDetails = execution.input || execution.output;

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <div
        className={cn(
          'rounded border bg-background/50',
          execution.status === 'error' && 'border-destructive/30'
        )}
      >
        <CollapsibleTrigger asChild>
          <button
            className="flex items-center gap-2 w-full px-3 py-2 text-xs hover:bg-muted/30 transition-colors text-left"
            disabled={!hasDetails}
          >
            {hasDetails ? (
              isOpen ? (
                <ChevronDown className="h-3 w-3 shrink-0" />
              ) : (
                <ChevronRight className="h-3 w-3 shrink-0" />
              )
            ) : (
              <div className="w-3" />
            )}

            {statusIcon}

            <span className="flex items-center gap-1 text-muted-foreground">
              {icon}
              <span className="font-medium">{label}</span>
            </span>

            {execution.tool_name !== execution.tool_type && (
              <span className="text-muted-foreground/70">
                ({execution.tool_name})
              </span>
            )}

            <span className="flex-1" />

            {execution.duration_ms && (
              <span className="flex items-center gap-0.5 text-muted-foreground/70">
                <Clock className="h-3 w-3" />
                {execution.duration_ms}ms
              </span>
            )}
          </button>
        </CollapsibleTrigger>

        {hasDetails && (
          <CollapsibleContent>
            <div className="px-3 pb-3 space-y-2 border-t border-border/50">
              {/* Input */}
              {execution.input && Object.keys(execution.input).length > 0 && (
                <div className="mt-2">
                  <div className="text-xs font-medium text-muted-foreground mb-1">
                    입력
                  </div>
                  <pre className="text-xs bg-muted/50 rounded p-2 overflow-x-auto whitespace-pre-wrap">
                    {JSON.stringify(execution.input, null, 2)}
                  </pre>
                </div>
              )}

              {/* Output */}
              {execution.output && (
                <div>
                  <div className="text-xs font-medium text-muted-foreground mb-1">
                    결과
                  </div>
                  <div className="text-xs bg-muted/50 rounded p-2 max-h-48 overflow-y-auto whitespace-pre-wrap">
                    {(() => {
                      const text = typeof execution.output === 'string'
                        ? execution.output
                        : typeof execution.output === 'object'
                          ? (execution.output as Record<string, unknown>).output as string || JSON.stringify(execution.output, null, 2)
                          : String(execution.output);
                      return text.length > 500 ? text.slice(0, 500) + '...' : text;
                    })()}
                  </div>
                </div>
              )}
            </div>
          </CollapsibleContent>
        )}
      </div>
    </Collapsible>
  );
}
