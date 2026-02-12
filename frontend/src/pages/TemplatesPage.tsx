import { LayoutTemplate } from 'lucide-react';
import { useTemplates } from '@/hooks/useTemplates';
import { TemplateCard } from '@/components/template/TemplateCard';

export function TemplatesPage() {
  const { templates, isLoading } = useTemplates();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">템플릿</h1>
        <p className="text-muted-foreground mt-1">
          Agent 생성에 사용할 수 있는 시스템 템플릿 목록입니다.
        </p>
      </div>

      {templates.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-center">
          <LayoutTemplate className="h-16 w-16 text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-semibold">아직 템플릿이 없습니다</h3>
          <p className="text-muted-foreground mt-2 max-w-md">
            관리자가 등록한 시스템 템플릿이 여기에 표시됩니다.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((template) => (
            <TemplateCard
              key={template.id}
              template={template}
            />
          ))}
        </div>
      )}
    </div>
  );
}
