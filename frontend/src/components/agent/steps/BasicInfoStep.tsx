import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useTemplates } from '@/hooks/useTemplates';
import type { AgentCreate } from '@/types';

interface BasicInfoStepProps {
  data: Partial<AgentCreate>;
  onChange: (data: Partial<AgentCreate>) => void;
}

export function BasicInfoStep({ data, onChange }: BasicInfoStepProps) {
  const { templates } = useTemplates();

  const handleTemplateChange = (val: string) => {
    if (val === 'none') {
      onChange({ template_id: undefined });
      return;
    }

    const selected = templates.find((t) => t.id === val);
    onChange({
      template_id: val,
      system_prompt: selected?.system_prompt_template || data.system_prompt,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-1">기본 정보</h3>
        <p className="text-sm text-muted-foreground">
          Agent의 이름, 설명, 시스템 프롬프트를 설정합니다.
        </p>
      </div>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="template">템플릿 (선택사항)</Label>
          <Select
            value={data.template_id || 'none'}
            onValueChange={handleTemplateChange}
          >
            <SelectTrigger>
              <SelectValue placeholder="템플릿을 선택하세요" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">직접 구성</SelectItem>
              {templates.map((t) => (
                <SelectItem key={t.id} value={t.id}>
                  {t.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-xs text-muted-foreground">
            템플릿을 선택하면 시스템 프롬프트가 자동 입력됩니다.
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="name">Agent 이름 *</Label>
          <Input
            id="name"
            value={data.name || ''}
            onChange={(e) => onChange({ name: e.target.value })}
            placeholder="예: 고객 상담 Agent"
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">설명</Label>
          <Input
            id="description"
            value={data.description || ''}
            onChange={(e) => onChange({ description: e.target.value })}
            placeholder="Agent의 역할을 설명하세요"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="systemPrompt">시스템 프롬프트</Label>
          <Textarea
            id="systemPrompt"
            value={data.system_prompt || ''}
            onChange={(e) => onChange({ system_prompt: e.target.value })}
            placeholder="Agent의 행동을 정의하는 시스템 프롬프트를 입력하세요..."
            rows={6}
          />
          <p className="text-xs text-muted-foreground">
            Agent가 어떤 역할로 응답할지, 어떤 톤으로 답변할지 등을 지시합니다.
          </p>
        </div>
      </div>
    </div>
  );
}
