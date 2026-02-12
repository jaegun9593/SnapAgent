import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import type { DashboardSummary } from '@/types';

interface CostEstimationCardProps {
  summary?: DashboardSummary;
  isLoading: boolean;
}

export function CostEstimationCard({
  summary,
  isLoading,
}: CostEstimationCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">비용 추정</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-24 w-full" />
        </CardContent>
      </Card>
    );
  }

  const totalCost = summary?.total_cost || 0;
  const totalTokens = summary?.total_tokens || 0;
  const totalCalls = summary?.total_calls || 0;
  const avgCostPerCall = totalCalls > 0 ? totalCost / totalCalls : 0;
  const avgTokensPerCall = totalCalls > 0 ? totalTokens / totalCalls : 0;

  const costItems = [
    {
      label: '총 추정 비용',
      value: `$${totalCost.toFixed(4)}`,
      description: '기간 내 전체 비용',
    },
    {
      label: '호출당 평균 비용',
      value: `$${avgCostPerCall.toFixed(6)}`,
      description: '호출 1회당 평균',
    },
    {
      label: '호출당 평균 토큰',
      value: avgTokensPerCall.toFixed(0),
      description: '호출 1회당 사용 토큰',
    },
    {
      label: '입력/출력 비율',
      value:
        summary && summary.total_prompt_tokens > 0
          ? `1:${(
              summary.total_completion_tokens / summary.total_prompt_tokens
            ).toFixed(2)}`
          : '-',
      description: '입력 대비 출력 토큰',
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">비용 추정</CardTitle>
        <CardDescription>
          {summary?.period
            ? `${summary.period.start_date} ~ ${summary.period.end_date}`
            : '기간 정보 없음'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {costItems.map((item) => (
            <div key={item.label} className="space-y-1">
              <p className="text-xs text-muted-foreground">{item.label}</p>
              <p className="text-lg font-bold">{item.value}</p>
              <p className="text-xs text-muted-foreground">{item.description}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
