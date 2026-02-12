import { useState } from 'react';
import { LayoutTemplate } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTemplates } from '@/hooks/useTemplates';
import { TemplateCard } from '@/components/template/TemplateCard';
import { TemplateCreateDialog } from '@/components/template/TemplateCreateDialog';

export function TemplatesPage() {
  const { templates, isLoading, deleteTemplateAsync, isDeleting } = useTemplates();
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">템플릿</h1>
          <p className="text-muted-foreground mt-1">
            Agent 생성에 사용할 수 있는 템플릿을 관리합니다.
          </p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)}>
          템플릿 생성
        </Button>
      </div>

      {templates.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-center">
          <LayoutTemplate className="h-16 w-16 text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-semibold">아직 템플릿이 없습니다</h3>
          <p className="text-muted-foreground mt-2 max-w-md">
            자주 사용하는 Agent 설정을 템플릿으로 저장하면
            빠르게 새 Agent를 만들 수 있습니다.
          </p>
          <Button className="mt-4" onClick={() => setIsCreateOpen(true)}>
            첫 템플릿 만들기
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((template) => (
            <TemplateCard
              key={template.id}
              template={template}
              onDelete={async () => {
                if (confirm('정말 이 템플릿을 삭제하시겠습니까?')) {
                  await deleteTemplateAsync(template.id);
                }
              }}
              isDeleting={isDeleting}
            />
          ))}
        </div>
      )}

      <TemplateCreateDialog
        open={isCreateOpen}
        onOpenChange={setIsCreateOpen}
      />
    </div>
  );
}
