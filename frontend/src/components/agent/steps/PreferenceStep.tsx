import { useState } from 'react';
import { Search, Globe, FileText, Activity, Pen, List, AlignLeft, FileBarChart, UserCheck, Smile, Briefcase } from 'lucide-react';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import type { AgentPreferences } from '@/types';

interface PreferenceStepProps {
  preferences: AgentPreferences;
  onChange: (preferences: AgentPreferences) => void;
}

interface OptionCard {
  value: string;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

const PURPOSE_OPTIONS: OptionCard[] = [
  { value: 'research', label: '정보 조사/리서치', description: '웹 검색으로 최신 정보 수집', icon: Globe },
  { value: 'qa', label: '문서 기반 Q&A', description: '업로드 문서에서 답변', icon: Search },
  { value: 'summary', label: '문서 요약/분석', description: '긴 문서를 핵심만 정리', icon: FileText },
  { value: 'monitoring', label: '실시간 모니터링', description: '주기적 웹 검색으로 변화 추적', icon: Activity },
  { value: 'custom', label: '직접 입력', description: '원하는 목적을 직접 작성', icon: Pen },
];

const FORMAT_OPTIONS: OptionCard[] = [
  { value: 'brief', label: '간단한 요약', description: '3-5문장 핵심 요약', icon: AlignLeft },
  { value: 'detailed', label: '상세 분석 리포트', description: '배경, 분석, 결론 포함', icon: FileBarChart },
  { value: 'list', label: '핵심 목록 + 링크', description: '번호 매기기 목록 정리', icon: List },
  { value: 'custom', label: '직접 입력', description: '원하는 형식을 직접 작성', icon: Pen },
];

const TONE_OPTIONS: OptionCard[] = [
  { value: 'formal', label: '공식적/전문적', description: '격식 있는 전문 어조', icon: Briefcase },
  { value: 'casual', label: '친근하고 캐주얼', description: '이해하기 쉬운 편안한 어조', icon: Smile },
  { value: 'professional', label: '친절하고 프로페셔널', description: '친절하면서도 전문적인 어조', icon: UserCheck },
  { value: 'custom', label: '직접 입력', description: '원하는 톤을 직접 작성', icon: Pen },
];

function SelectionGrid({
  title,
  description,
  options,
  selected,
  customValue,
  onSelect,
  onCustomChange,
}: {
  title: string;
  description: string;
  options: OptionCard[];
  selected: string;
  customValue: string;
  onSelect: (value: string) => void;
  onCustomChange: (value: string) => void;
}) {
  const isCustom = selected === 'custom';

  return (
    <div className="space-y-3">
      <div>
        <h3 className="text-base font-semibold">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      <div className="grid grid-cols-2 gap-3">
        {options.map((option) => {
          const Icon = option.icon;
          const isSelected = selected === option.value;
          return (
            <button
              key={option.value}
              type="button"
              onClick={() => onSelect(option.value)}
              className={cn(
                'flex items-start gap-3 rounded-lg border p-3 text-left transition-colors hover:bg-accent/50',
                isSelected
                  ? 'border-primary bg-primary/5'
                  : 'border-border'
              )}
            >
              <Icon className={cn('mt-0.5 h-5 w-5 flex-shrink-0', isSelected ? 'text-primary' : 'text-muted-foreground')} />
              <div className="min-w-0">
                <div className={cn('text-sm font-medium', isSelected ? 'text-primary' : '')}>{option.label}</div>
                <div className="text-xs text-muted-foreground">{option.description}</div>
              </div>
            </button>
          );
        })}
      </div>
      {isCustom && (
        <Textarea
          placeholder="직접 입력하세요..."
          value={customValue}
          onChange={(e) => onCustomChange(e.target.value)}
          rows={3}
          className="mt-2"
        />
      )}
    </div>
  );
}

export function PreferenceStep({ preferences, onChange }: PreferenceStepProps) {
  // Track which fields are in custom mode (separate from value)
  const [customMode, setCustomMode] = useState<Record<string, boolean>>(() => {
    const initial: Record<string, boolean> = {};
    const allOptions = { task_purpose: PURPOSE_OPTIONS, response_format: FORMAT_OPTIONS, response_tone: TONE_OPTIONS };
    for (const [field, options] of Object.entries(allOptions)) {
      const val = preferences[field as keyof AgentPreferences];
      if (val && !options.some((o) => o.value === val && o.value !== 'custom')) {
        initial[field] = true;
      }
    }
    return initial;
  });

  const getSelected = (field: keyof AgentPreferences, options: OptionCard[]) => {
    if (customMode[field]) return 'custom';
    const value = preferences[field];
    if (!value) return '';
    if (options.some((o) => o.value === value && o.value !== 'custom')) return value;
    return '';
  };

  const handleSelect = (field: keyof AgentPreferences, value: string) => {
    if (value === 'custom') {
      setCustomMode((prev) => ({ ...prev, [field]: true }));
      onChange({ ...preferences, [field]: '' });
    } else {
      setCustomMode((prev) => ({ ...prev, [field]: false }));
      onChange({ ...preferences, [field]: value });
    }
  };

  const handleCustomChange = (field: keyof AgentPreferences, value: string) => {
    onChange({ ...preferences, [field]: value });
  };

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold mb-1">선호 설정</h3>
        <p className="text-sm text-muted-foreground">
          Agent의 목적, 응답 형식, 응답 톤을 설정합니다. 이 설정은 시스템 프롬프트와 의도 분류에 반영됩니다.
        </p>
      </div>

      <SelectionGrid
        title="Agent 목적"
        description="이 Agent의 주요 사용 목적을 선택하세요"
        options={PURPOSE_OPTIONS}
        selected={getSelected('task_purpose', PURPOSE_OPTIONS)}
        customValue={customMode.task_purpose ? preferences.task_purpose : ''}
        onSelect={(v) => handleSelect('task_purpose', v)}
        onCustomChange={(v) => handleCustomChange('task_purpose', v)}
      />

      <SelectionGrid
        title="응답 형식"
        description="Agent가 답변할 때 사용할 형식을 선택하세요"
        options={FORMAT_OPTIONS}
        selected={getSelected('response_format', FORMAT_OPTIONS)}
        customValue={customMode.response_format ? preferences.response_format : ''}
        onSelect={(v) => handleSelect('response_format', v)}
        onCustomChange={(v) => handleCustomChange('response_format', v)}
      />

      <SelectionGrid
        title="응답 톤"
        description="Agent가 답변할 때 사용할 어조를 선택하세요"
        options={TONE_OPTIONS}
        selected={getSelected('response_tone', TONE_OPTIONS)}
        customValue={customMode.response_tone ? preferences.response_tone : ''}
        onSelect={(v) => handleSelect('response_tone', v)}
        onCustomChange={(v) => handleCustomChange('response_tone', v)}
      />
    </div>
  );
}
