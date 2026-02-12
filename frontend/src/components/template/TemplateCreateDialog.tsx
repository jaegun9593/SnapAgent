import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useTemplates } from '@/hooks/useTemplates';

interface TemplateCreateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TemplateCreateDialog({
  open,
  onOpenChange,
}: TemplateCreateDialogProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [systemPromptTemplate, setSystemPromptTemplate] = useState('');
  const { createTemplateAsync, isCreating } = useTemplates();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      await createTemplateAsync({
        name: name.trim(),
        description: description.trim() || undefined,
        category: category.trim() || undefined,
        system_prompt_template: systemPromptTemplate.trim() || undefined,
      });
      // Reset form
      setName('');
      setDescription('');
      setCategory('');
      setSystemPromptTemplate('');
      onOpenChange(false);
    } catch (err) {
      console.error('Failed to create template:', err);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>템플릿 생성</DialogTitle>
          <DialogDescription>
            Agent 생성에 사용할 수 있는 새 템플릿을 만듭니다.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">템플릿 이름 *</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="예: 고객 상담 템플릿"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">설명</Label>
            <Input
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="템플릿의 용도를 설명하세요"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="category">카테고리</Label>
            <Input
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="예: 고객지원, 분석, 검색"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="systemPrompt">시스템 프롬프트 템플릿</Label>
            <Textarea
              id="systemPrompt"
              value={systemPromptTemplate}
              onChange={(e) => setSystemPromptTemplate(e.target.value)}
              placeholder="기본 시스템 프롬프트를 입력하세요..."
              rows={5}
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              취소
            </Button>
            <Button type="submit" disabled={isCreating || !name.trim()}>
              {isCreating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  생성 중...
                </>
              ) : (
                '생성'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
