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
import type { AgentCreate, AgentPreferences } from '@/types';

interface BasicInfoStepProps {
  data: Partial<AgentCreate>;
  onChange: (data: Partial<AgentCreate>) => void;
  preferences?: AgentPreferences;
}

const PURPOSE_LABELS: Record<string, string> = {
  research: '정보 조사/리서치',
  qa: '문서 기반 Q&A',
  summary: '문서 요약/분석',
  monitoring: '실시간 모니터링',
};

const FORMAT_LABELS: Record<string, string> = {
  brief: '간단한 요약',
  detailed: '상세 분석 리포트',
  list: '핵심 목록 + 링크',
};

const TONE_LABELS: Record<string, string> = {
  formal: '공식적/전문적',
  casual: '친근하고 캐주얼',
  professional: '친절하고 프로페셔널',
};

function labelFor(value: string, map: Record<string, string>): string {
  return map[value] || value || '-';
}

export function BasicInfoStep({ data, onChange, preferences }: BasicInfoStepProps) {
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

  const hasPreferences = preferences && (preferences.task_purpose || preferences.response_format || preferences.response_tone);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-1">기본 정보</h3>
        <p className="text-sm text-muted-foreground">
          Agent의 이름, 설명, 시스템 프롬프트를 설정합니다.
        </p>
      </div>

      <div className="space-y-4">
        {hasPreferences && (
          <div className="rounded-lg border bg-muted/50 p-4 space-y-2">
            <h4 className="text-sm font-medium text-muted-foreground">선호 설정 요약</h4>
            <div className="grid grid-cols-3 gap-2 text-sm">
              <div>
                <span className="text-muted-foreground">목적: </span>
                <span className="font-medium">{labelFor(preferences.task_purpose, PURPOSE_LABELS)}</span>
              </div>
              <div>
                <span className="text-muted-foreground">형식: </span>
                <span className="font-medium">{labelFor(preferences.response_format, FORMAT_LABELS)}</span>
              </div>
              <div>
                <span className="text-muted-foreground">톤: </span>
                <span className="font-medium">{labelFor(preferences.response_tone, TONE_LABELS)}</span>
              </div>
            </div>
          </div>
        )}

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
            선호 설정에 따른 지시문이 자동으로 앞에 추가됩니다.
          </p>
        </div>
      </div>
    </div>
  );
}
