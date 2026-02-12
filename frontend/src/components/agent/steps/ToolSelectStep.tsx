import { Search, Globe, Plug } from 'lucide-react';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import type { AgentToolConfig } from '@/types';

interface ToolSelectStepProps {
  tools: AgentToolConfig[];
  onChange: (tools: AgentToolConfig[]) => void;
}

const AVAILABLE_TOOLS = [
  {
    type: 'rag' as const,
    name: 'RAG (문서 검색)',
    description: '업로드한 문서에서 관련 정보를 검색합니다.',
    icon: Search,
  },
  {
    type: 'web_search' as const,
    name: '웹 검색',
    description: 'DuckDuckGo를 통해 인터넷에서 실시간 정보를 검색합니다.',
    icon: Globe,
  },
  {
    type: 'custom_api' as const,
    name: '외부 API',
    description: '사용자 정의 REST API를 호출합니다.',
    icon: Plug,
  },
];

export function ToolSelectStep({ tools, onChange }: ToolSelectStepProps) {
  const isToolEnabled = (toolType: string) =>
    tools.some((t) => t.tool_type === toolType && t.is_enabled);

  const getToolConfig = (toolType: string) =>
    tools.find((t) => t.tool_type === toolType);

  const toggleTool = (toolType: 'rag' | 'web_search' | 'custom_api') => {
    if (isToolEnabled(toolType)) {
      onChange(tools.filter((t) => t.tool_type !== toolType));
    } else {
      onChange([
        ...tools,
        {
          tool_type: toolType,
          is_enabled: true,
          sort_order: tools.length,
          tool_config: toolType === 'custom_api' ? { url: '', method: 'GET' } : undefined,
        },
      ]);
    }
  };

  const updateToolConfig = (
    toolType: string,
    config: Record<string, unknown>
  ) => {
    onChange(
      tools.map((t) =>
        t.tool_type === toolType ? { ...t, tool_config: config } : t
      )
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-1">도구 선택</h3>
        <p className="text-sm text-muted-foreground">
          Agent가 사용할 도구를 선택합니다. 여러 도구를 동시에 활성화할 수 있습니다.
        </p>
      </div>

      <div className="space-y-4">
        {AVAILABLE_TOOLS.map((tool) => {
          const Icon = tool.icon;
          const enabled = isToolEnabled(tool.type);
          const config = getToolConfig(tool.type);

          return (
            <Card
              key={tool.type}
              className={enabled ? 'border-primary' : ''}
            >
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <Checkbox
                    checked={enabled}
                    onCheckedChange={() => toggleTool(tool.type)}
                  />
                  <Icon className="h-5 w-5 text-primary" />
                  <div className="flex-1">
                    <CardTitle className="text-base">{tool.name}</CardTitle>
                    <CardDescription className="text-xs">
                      {tool.description}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              {enabled && tool.type === 'custom_api' && (
                <CardContent className="space-y-3">
                  <div className="space-y-2">
                    <Label className="text-xs">API URL</Label>
                    <Input
                      placeholder="https://api.example.com/endpoint"
                      value={(config?.tool_config as Record<string, string>)?.url || ''}
                      onChange={(e) =>
                        updateToolConfig(tool.type, {
                          ...(config?.tool_config || {}),
                          url: e.target.value,
                        })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs">HTTP Method</Label>
                    <Input
                      placeholder="GET"
                      value={(config?.tool_config as Record<string, string>)?.method || 'GET'}
                      onChange={(e) =>
                        updateToolConfig(tool.type, {
                          ...(config?.tool_config || {}),
                          method: e.target.value,
                        })
                      }
                    />
                  </div>
                </CardContent>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}
