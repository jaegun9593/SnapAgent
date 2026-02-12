import { useState } from 'react';
import { Send, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useAgentTest } from '@/hooks/useAgents';
import { ToolExecutionLayer } from '@/components/chat/ToolExecutionLayer';
import type { ToolExecution } from '@/types';

interface TestStepProps {
  agentId: string;
}

export function TestStep({ agentId }: TestStepProps) {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<{
    success: boolean;
    response?: string;
    tool_calls?: Record<string, unknown>[];
    token_usage?: Record<string, number>;
    latency_ms?: number;
    error?: string;
  } | null>(null);

  const testMutation = useAgentTest();

  const handleTest = async () => {
    if (!query.trim()) return;

    try {
      const res = await testMutation.mutateAsync({
        agentId,
        data: { query },
      });
      setResult(res);
    } catch (err) {
      console.error('Test failed:', err);
    }
  };

  // Convert tool_calls from test response to ToolExecution format
  const toolExecutions: ToolExecution[] =
    result?.tool_calls?.map((tc) => ({
      tool_type: (tc.tool_type as string) || 'unknown',
      tool_name: (tc.tool_name as string) || 'unknown',
      input: tc.input as Record<string, unknown>,
      output: (tc.output as string) || '',
      status: 'completed' as const,
    })) || [];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-1">Agent 테스트</h3>
        <p className="text-sm text-muted-foreground">
          생성된 Agent에 테스트 질문을 보내 정상 동작을 확인합니다.
        </p>
      </div>

      {/* Test Input */}
      <div className="flex gap-2">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="테스트 질문을 입력하세요..."
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleTest();
          }}
        />
        <Button onClick={handleTest} disabled={testMutation.isPending || !query.trim()}>
          {testMutation.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Test Result */}
      {result && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              {result.success ? (
                <CheckCircle2 className="h-5 w-5 text-green-500" />
              ) : (
                <AlertCircle className="h-5 w-5 text-destructive" />
              )}
              <CardTitle className="text-base">
                {result.success ? '테스트 성공' : '테스트 실패'}
              </CardTitle>
              {result.latency_ms && (
                <Badge variant="outline" className="text-xs">
                  {result.latency_ms}ms
                </Badge>
              )}
            </div>
            {result.token_usage && (
              <CardDescription>
                토큰 사용: 입력 {result.token_usage.prompt_tokens || 0} / 출력{' '}
                {result.token_usage.completion_tokens || 0}
              </CardDescription>
            )}
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Tool Executions */}
            {toolExecutions.length > 0 && (
              <ToolExecutionLayer
                executions={toolExecutions}
                isCollapsible={true}
              />
            )}

            {/* Response */}
            {result.response && (
              <div className="rounded-md bg-muted p-4 text-sm whitespace-pre-wrap">
                {result.response}
              </div>
            )}

            {/* Error */}
            {result.error && (
              <div className="rounded-md bg-destructive/10 p-4 text-sm text-destructive">
                {result.error}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <p className="text-xs text-muted-foreground">
        테스트를 건너뛰고 바로 채팅을 시작할 수도 있습니다.
      </p>
    </div>
  );
}
