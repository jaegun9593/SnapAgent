import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import type { DashboardSummary } from '@/types';

interface UsageSummaryCardProps {
  summary?: DashboardSummary;
  isLoading: boolean;
}

export function UsageSummaryCard({ summary, isLoading }: UsageSummaryCardProps) {
  const stats = [
    {
      title: '총 호출 수',
      value: summary?.total_calls || 0,
      format: (v: number) => v.toLocaleString(),
    },
    {
      title: '입력 토큰',
      value: summary?.total_prompt_tokens || 0,
      format: (v: number) => v.toLocaleString(),
    },
    {
      title: '출력 토큰',
      value: summary?.total_completion_tokens || 0,
      format: (v: number) => v.toLocaleString(),
    },
    {
      title: '전체 토큰',
      value: summary?.total_tokens || 0,
      format: (v: number) => v.toLocaleString(),
    },
    {
      title: '추정 비용',
      value: summary?.total_cost || 0,
      format: (v: number) => `$${v.toFixed(4)}`,
    },
    {
      title: '평균 지연시간',
      value: summary?.avg_latency_ms || 0,
      format: (v: number) => `${v}ms`,
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {stats.map((stat) => (
        <Card key={stat.title}>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              {stat.title}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <div className="text-xl font-bold">
                {stat.format(stat.value)}
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
