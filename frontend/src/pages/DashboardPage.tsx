import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useAgents } from '@/hooks/useAgents';
import {
  useDashboardSummary,
  useDashboardTimeseries,
  useDashboardByAgent,
} from '@/hooks/useDashboard';
import { UsageSummaryCard } from '@/components/dashboard/UsageSummaryCard';
import { TokenUsageChart } from '@/components/dashboard/TokenUsageChart';
import { AgentCallChart } from '@/components/dashboard/AgentCallChart';
import { CostEstimationCard } from '@/components/dashboard/CostEstimationCard';

export function DashboardPage() {
  const [selectedAgent, setSelectedAgent] = useState<string>('all');

  const { agents, isLoading: agentsLoading } = useAgents();

  const agentFilter =
    selectedAgent !== 'all' ? { agent_id: selectedAgent } : undefined;

  const { data: summary, isLoading: summaryLoading } =
    useDashboardSummary(agentFilter);
  const { data: timeseries, isLoading: timeseriesLoading } =
    useDashboardTimeseries(agentFilter);
  const { data: byAgent, isLoading: byAgentLoading } = useDashboardByAgent();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">대시보드</h1>
        <p className="text-muted-foreground mt-1">
          사용량 통계와 비용을 확인합니다.
        </p>
      </div>

      {/* Resource Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Agent 수
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {agentsLoading ? '...' : agents.length}
            </div>
            <p className="text-xs text-muted-foreground mt-1">등록된 Agent</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              총 호출 수
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {summaryLoading ? '...' : summary?.total_calls || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">API 호출 횟수</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              총 토큰 사용량
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {summaryLoading
                ? '...'
                : (summary?.total_tokens || 0).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground mt-1">전체 토큰</p>
          </CardContent>
        </Card>
      </div>

      {/* Usage Summary Cards */}
      <UsageSummaryCard summary={summary} isLoading={summaryLoading} />

      {/* Agent Filter */}
      <div className="flex items-center gap-4">
        <span className="text-sm font-medium">Agent 필터:</span>
        <Select value={selectedAgent} onValueChange={setSelectedAgent}>
          <SelectTrigger className="w-[250px]">
            <SelectValue placeholder="전체 Agent" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">전체 Agent</SelectItem>
            {agents?.map((agent) => (
              <SelectItem key={agent.id} value={agent.id}>
                {agent.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TokenUsageChart
          data={timeseries?.data || []}
          isLoading={timeseriesLoading}
        />
        <AgentCallChart
          data={byAgent?.data || []}
          isLoading={byAgentLoading}
        />
      </div>

      {/* Cost Card */}
      <CostEstimationCard summary={summary} isLoading={summaryLoading} />
    </div>
  );
}
