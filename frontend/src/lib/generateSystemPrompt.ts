import type { AgentPreferences } from '@/types';

const PURPOSE_MAP: Record<string, string> = {
  research: '웹 검색을 활용하여 최신 정보를 조사하고 출처와 함께 정리하세요.',
  qa: '제공된 문서를 기반으로 정확하고 근거 있는 답변을 제공하세요.',
  summary: '핵심 내용을 중심으로 간결하게 요약하고 분석하세요.',
  monitoring: '최신 변화를 주기적으로 확인하고 중요 변경사항을 알려주세요.',
};

const FORMAT_MAP: Record<string, string> = {
  brief: '답변은 3-5문장으로 간결하게 요약하세요.',
  detailed: '배경, 분석, 결론을 포함한 상세한 리포트 형식으로 답변하세요.',
  list: '핵심 포인트를 번호 매기기 목록으로 정리하고, 관련 링크가 있으면 포함하세요.',
};

const TONE_MAP: Record<string, string> = {
  formal: '공식적이고 전문적인 어조로 답변하세요.',
  casual: '친근하고 이해하기 쉬운 캐주얼한 어조로 답변하세요.',
  professional: '친절하면서도 전문적인 어조로 답변하세요.',
};

export function generateSystemPrompt(prefs: AgentPreferences): string {
  const parts: string[] = [];

  if (prefs.task_purpose) {
    parts.push(PURPOSE_MAP[prefs.task_purpose] || prefs.task_purpose);
  }
  if (prefs.response_format) {
    parts.push(FORMAT_MAP[prefs.response_format] || prefs.response_format);
  }
  if (prefs.response_tone) {
    parts.push(TONE_MAP[prefs.response_tone] || prefs.response_tone);
  }

  return parts.join('\n');
}
