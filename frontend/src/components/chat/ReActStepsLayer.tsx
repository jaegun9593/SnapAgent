import { useState } from 'react';
import {
  ChevronDown,
  ChevronRight,
  Brain,
  Search,
  Globe,
  Plug,
  CheckCircle2,
  Loader2,
  BarChart3,
  Zap,
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
import type { ReActStep } from '@/types';

interface ReActStepsLayerProps {
  steps: ReActStep[];
  isStreaming: boolean;
}

const intentLabels: Record<string, string> = {
  general_chat: '일반 대화',
  rag_search: 'RAG 검색',
  web_search: '웹 검색',
  hybrid: '하이브리드 검색',
  unknown: '분석 중',
};

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

function StepItem({ step }: { step: ReActStep }) {
  const [isOpen, setIsOpen] = useState(false);

  if (step.type === 'intent') {
    const intent = step.data.intent as string;
    const confidence = step.data.confidence as number;
    const content = step.data.content as string;

    return (
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <div className="rounded border bg-background/50">
          <CollapsibleTrigger asChild>
            <button className="flex items-center gap-2 w-full px-3 py-2 text-xs hover:bg-muted/30 transition-colors text-left">
              {isOpen ? (
                <ChevronDown className="h-3 w-3 shrink-0" />
              ) : (
                <ChevronRight className="h-3 w-3 shrink-0" />
              )}
              <Brain className="h-3.5 w-3.5 text-violet-500 shrink-0" />
              <span className="font-medium text-muted-foreground">의도 분류</span>
              <Badge variant="secondary" className="text-xs px-1.5 py-0">
                {intentLabels[intent] || intent}
              </Badge>
              <span className="flex-1" />
              <span className="text-muted-foreground/70">
                {(confidence * 100).toFixed(0)}%
              </span>
            </button>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="px-3 pb-3 border-t border-border/50">
              <p className="mt-2 text-xs text-muted-foreground">{content}</p>
            </div>
          </CollapsibleContent>
        </div>
      </Collapsible>
    );
  }

  if (step.type === 'tool') {
    const toolType = step.data.tool_type as string;
    const toolName = step.data.tool_name as string;
    const input = step.data.input as Record<string, unknown> | undefined;
    const output = step.data.output as string | undefined;
    const durationMs = step.data.duration_ms as number | undefined;
    const icon = toolIcons[toolType] || <Plug className="h-3.5 w-3.5" />;
    const label = toolLabels[toolType] || toolName;
    const isRunning = step.status === 'running';

    return (
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <div className={cn('rounded border bg-background/50', step.status === 'error' && 'border-destructive/30')}>
          <CollapsibleTrigger asChild>
            <button className="flex items-center gap-2 w-full px-3 py-2 text-xs hover:bg-muted/30 transition-colors text-left">
              {isOpen ? (
                <ChevronDown className="h-3 w-3 shrink-0" />
              ) : (
                <ChevronRight className="h-3 w-3 shrink-0" />
              )}
              {isRunning ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin text-primary shrink-0" />
              ) : (
                <CheckCircle2 className="h-3.5 w-3.5 text-green-500 shrink-0" />
              )}
              <span className="flex items-center gap-1 text-muted-foreground">
                {icon}
                <span className="font-medium">{label}</span>
              </span>
              <span className="flex-1" />
              {durationMs && (
                <span className="text-muted-foreground/70">{durationMs}ms</span>
              )}
              {isRunning && (
                <span className="text-muted-foreground/70">실행 중...</span>
              )}
            </button>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="px-3 pb-3 space-y-2 border-t border-border/50">
              {input && Object.keys(input).length > 0 && (
                <div className="mt-2">
                  <div className="text-xs font-medium text-muted-foreground mb-1">입력</div>
                  <pre className="text-xs bg-muted/50 rounded p-2 overflow-x-auto whitespace-pre-wrap">
                    {JSON.stringify(input, null, 2)}
                  </pre>
                </div>
              )}
              {output && (
                <div>
                  <div className="text-xs font-medium text-muted-foreground mb-1">결과</div>
                  <div className="text-xs bg-muted/50 rounded p-2 max-h-48 overflow-y-auto whitespace-pre-wrap">
                    {typeof output === 'string'
                      ? output.length > 500
                        ? output.slice(0, 500) + '...'
                        : output
                      : JSON.stringify(output, null, 2).slice(0, 500)}
                  </div>
                </div>
              )}
            </div>
          </CollapsibleContent>
        </div>
      </Collapsible>
    );
  }

  if (step.type === 'evaluation') {
    const score = step.data.score as number;
    const reasoning = step.data.reasoning as string;
    const needsRetry = step.data.needs_retry as boolean;

    return (
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <div className="rounded border bg-background/50">
          <CollapsibleTrigger asChild>
            <button className="flex items-center gap-2 w-full px-3 py-2 text-xs hover:bg-muted/30 transition-colors text-left">
              {isOpen ? (
                <ChevronDown className="h-3 w-3 shrink-0" />
              ) : (
                <ChevronRight className="h-3 w-3 shrink-0" />
              )}
              <BarChart3 className={cn(
                'h-3.5 w-3.5 shrink-0',
                needsRetry ? 'text-amber-500' : 'text-green-500'
              )} />
              <span className="font-medium text-muted-foreground">답변 평가</span>
              <Badge
                variant={needsRetry ? 'outline' : 'secondary'}
                className={cn(
                  'text-xs px-1.5 py-0',
                  !needsRetry && 'bg-green-500/10 text-green-600 border-green-500/20'
                )}
              >
                {(score * 100).toFixed(0)}%
                {needsRetry ? ' 재시도' : ' 통과'}
              </Badge>
            </button>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="px-3 pb-3 border-t border-border/50">
              <p className="mt-2 text-xs text-muted-foreground">{reasoning}</p>
            </div>
          </CollapsibleContent>
        </div>
      </Collapsible>
    );
  }

  return null;
}

export function ReActStepsLayer({ steps, isStreaming }: ReActStepsLayerProps) {
  const [isOpen, setIsOpen] = useState(true);

  if (steps.length === 0) return null;

  const intentSteps = steps.filter((s) => s.type === 'intent');
  const toolSteps = steps.filter((s) => s.type === 'tool');
  const evalSteps = steps.filter((s) => s.type === 'evaluation');
  const allDone = !isStreaming;

  const summaryParts: string[] = [];
  if (intentSteps.length > 0) {
    const lastIntent = intentSteps[intentSteps.length - 1];
    const intent = lastIntent.data.intent as string;
    summaryParts.push(intentLabels[intent] || intent);
  }
  if (toolSteps.length > 0) {
    summaryParts.push(`도구 ${toolSteps.length}개`);
  }
  const summaryText = allDone
    ? `ReAct 완료 — ${summaryParts.join(', ')}`
    : `ReAct 처리 중 — ${summaryParts.join(', ')}`;

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <div className="rounded-md border bg-muted/30 overflow-hidden">
        <CollapsibleTrigger asChild>
          <button className="flex items-center gap-2 w-full px-3 py-2 text-sm transition-colors hover:bg-muted/50 text-left">
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

            <Zap className="h-4 w-4 text-amber-500 shrink-0" />

            <span className="font-medium text-muted-foreground flex-1">
              {summaryText}
            </span>

            <div className="flex items-center gap-1">
              {intentSteps.length > 0 && (
                <Badge variant="secondary" className="text-xs px-1.5 py-0">
                  <Brain className="h-3 w-3 mr-0.5" />
                  의도
                </Badge>
              )}
              {toolSteps.map((s, i) => (
                <Badge key={i} variant="secondary" className="text-xs px-1.5 py-0">
                  {toolIcons[s.data.tool_type as string] || <Plug className="h-3 w-3" />}
                  <span className="ml-0.5">
                    {toolLabels[s.data.tool_type as string] || s.data.tool_name as string}
                  </span>
                </Badge>
              ))}
              {evalSteps.length > 0 && (
                <Badge variant="secondary" className="text-xs px-1.5 py-0">
                  <BarChart3 className="h-3 w-3 mr-0.5" />
                  평가
                </Badge>
              )}
            </div>
          </button>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <div className="px-3 pb-3 pt-1 border-t border-border/50 space-y-2">
            {steps.map((step, idx) => (
              <StepItem key={idx} step={step} />
            ))}
          </div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
}
