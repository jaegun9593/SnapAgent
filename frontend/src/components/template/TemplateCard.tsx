import { LayoutTemplate, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
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
import type { Template } from '@/types';

interface TemplateCardProps {
  template: Template;
}

export function TemplateCard({ template }: TemplateCardProps) {
  const navigate = useNavigate();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <LayoutTemplate className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">{template.name}</CardTitle>
          </div>
          <div className="flex gap-1">
            {template.is_system && (
              <Badge variant="secondary" className="text-xs">
                시스템
              </Badge>
            )}
            {template.category && (
              <Badge variant="outline" className="text-xs">
                {template.category}
              </Badge>
            )}
          </div>
        </div>
        <CardDescription className="line-clamp-2">
          {template.description || '설명 없음'}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-1">
        {template.system_prompt_template && (
          <div className="text-xs text-muted-foreground bg-muted rounded p-2 line-clamp-3">
            {template.system_prompt_template}
          </div>
        )}
        <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
          <Clock className="h-3 w-3" />
          <span>{formatDate(template.updated_at)}</span>
        </div>
      </CardContent>
      <CardFooter>
        <Button
          className="w-full"
          variant="outline"
          onClick={() =>
            navigate('/agents/create', {
              state: { templateId: template.id },
            })
          }
        >
          이 템플릿으로 Agent 생성
        </Button>
      </CardFooter>
    </Card>
  );
}
