import type { ToolType } from '@/types';

export interface ToolInfo {
  type: ToolType;
  name: string;
  description: string;
  icon: string; // lucide-react icon name reference
  requiresConfig: boolean;
  configFields?: {
    key: string;
    label: string;
    placeholder: string;
    type: 'text' | 'number' | 'select';
    defaultValue?: string;
  }[];
}

export interface ToolCategory {
  id: string;
  name: string;
  description: string;
  tools: ToolInfo[];
}

// Purpose → recommended tool types mapping
export const PURPOSE_TOOL_MAP: Record<string, ToolType[]> = {
  research: ['web_search', 'tavily_search', 'wikipedia', 'web_scraper'],
  qa: ['rag'],
  summary: ['rag', 'web_scraper'],
  monitoring: ['web_search', 'tavily_search', 'web_scraper'],
};

export const TOOL_CATEGORIES: ToolCategory[] = [
  {
    id: 'web',
    name: '웹 검색',
    description: '인터넷에서 정보를 검색합니다',
    tools: [
      {
        type: 'web_search',
        name: '웹 검색 (DuckDuckGo)',
        description: '무료 웹 검색, API 키 불필요',
        icon: 'Globe',
        requiresConfig: false,
      },
      {
        type: 'tavily_search',
        name: 'Tavily 검색',
        description: 'AI 최적화 고급 웹 검색 (API 키 필요)',
        icon: 'Sparkles',
        requiresConfig: true,
        configFields: [
          {
            key: 'api_key',
            label: 'Tavily API Key',
            placeholder: 'tvly-...',
            type: 'text',
          },
          {
            key: 'search_depth',
            label: '검색 깊이',
            placeholder: 'basic',
            type: 'select',
            defaultValue: 'basic',
          },
        ],
      },
    ],
  },
  {
    id: 'document',
    name: '문서/RAG',
    description: '업로드된 문서에서 정보를 검색합니다',
    tools: [
      {
        type: 'rag',
        name: 'RAG 문서 검색',
        description: '업로드 문서에서 벡터 유사도 검색',
        icon: 'FileSearch',
        requiresConfig: false,
      },
    ],
  },
  {
    id: 'academic',
    name: '학술/정보',
    description: '학술 자료 및 백과사전을 검색합니다',
    tools: [
      {
        type: 'wikipedia',
        name: 'Wikipedia',
        description: '위키피디아 문서 검색',
        icon: 'BookOpen',
        requiresConfig: false,
      },
      {
        type: 'arxiv',
        name: 'ArXiv 논문',
        description: '학술 논문 검색 (제목, 초록, PDF)',
        icon: 'GraduationCap',
        requiresConfig: false,
      },
    ],
  },
  {
    id: 'code',
    name: '코드/계산',
    description: '수식 계산 및 코드 실행',
    tools: [
      {
        type: 'calculator',
        name: '계산기',
        description: '수학 수식 계산',
        icon: 'Calculator',
        requiresConfig: false,
      },
      {
        type: 'python_repl',
        name: 'Python 실행',
        description: 'Python 코드 실행 (샌드박스)',
        icon: 'Terminal',
        requiresConfig: false,
      },
    ],
  },
  {
    id: 'data',
    name: '데이터 수집',
    description: '외부 데이터를 수집합니다',
    tools: [
      {
        type: 'web_scraper',
        name: '웹 스크래퍼',
        description: '웹 페이지에서 텍스트 추출',
        icon: 'FileDown',
        requiresConfig: false,
      },
      {
        type: 'custom_api',
        name: '외부 API',
        description: '사용자 정의 REST API 호출',
        icon: 'Plug',
        requiresConfig: true,
        configFields: [
          {
            key: 'url',
            label: 'API URL',
            placeholder: 'https://api.example.com/endpoint',
            type: 'text',
          },
          {
            key: 'method',
            label: 'HTTP Method',
            placeholder: 'GET',
            type: 'text',
            defaultValue: 'GET',
          },
        ],
      },
    ],
  },
];

/** Flatten all tools from categories */
export function getAllTools(): ToolInfo[] {
  return TOOL_CATEGORIES.flatMap((cat) => cat.tools);
}

/** Check if a tool is recommended for the given purpose */
export function isRecommended(toolType: ToolType, taskPurpose?: string): boolean {
  if (!taskPurpose) return false;
  const recommended = PURPOSE_TOOL_MAP[taskPurpose];
  return recommended ? recommended.includes(toolType) : false;
}
