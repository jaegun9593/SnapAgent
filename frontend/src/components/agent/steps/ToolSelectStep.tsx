import {
  Globe, Sparkles, FileSearch, BookOpen, GraduationCap,
  Calculator, Terminal, FileDown, Plug, Star,
} from 'lucide-react';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { TOOL_CATEGORIES, isRecommended } from '@/lib/toolCatalog';
import type { AgentToolConfig, ToolType } from '@/types';
import type { ToolInfo } from '@/lib/toolCatalog';

interface ToolSelectStepProps {
  tools: AgentToolConfig[];
  onChange: (tools: AgentToolConfig[]) => void;
  taskPurpose?: string;
}

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  Globe,
  Sparkles,
  FileSearch,
  BookOpen,
  GraduationCap,
  Calculator,
  Terminal,
  FileDown,
  Plug,
};

export function ToolSelectStep({ tools, onChange, taskPurpose }: ToolSelectStepProps) {
  const isToolEnabled = (toolType: string) =>
    tools.some((t) => t.tool_type === toolType && t.is_enabled);

  const getToolConfig = (toolType: string) =>
    tools.find((t) => t.tool_type === toolType);

  const toggleTool = (toolType: ToolType) => {
    if (isToolEnabled(toolType)) {
      onChange(tools.filter((t) => t.tool_type !== toolType));
    } else {
      const toolInfo = TOOL_CATEGORIES
        .flatMap((c) => c.tools)
        .find((t) => t.type === toolType);

      const defaultConfig: Record<string, unknown> | undefined =
        toolInfo?.configFields
          ? Object.fromEntries(
              toolInfo.configFields
                .filter((f) => f.defaultValue)
                .map((f) => [f.key, f.defaultValue])
            )
          : undefined;

      onChange([
        ...tools,
        {
          tool_type: toolType,
          is_enabled: true,
          sort_order: tools.length,
          tool_config: defaultConfig && Object.keys(defaultConfig).length > 0
            ? defaultConfig
            : undefined,
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

  const renderConfigFields = (toolInfo: ToolInfo, config: AgentToolConfig | undefined) => {
    if (!toolInfo.configFields) return null;

    return (
      <CardContent className="space-y-3">
        {toolInfo.configFields.map((field) => (
          <div key={field.key} className="space-y-2">
            <Label className="text-xs">{field.label}</Label>
            <Input
              placeholder={field.placeholder}
              value={
                (config?.tool_config as Record<string, string>)?.[field.key] ||
                field.defaultValue ||
                ''
              }
              onChange={(e) =>
                updateToolConfig(toolInfo.type, {
                  ...(config?.tool_config || {}),
                  [field.key]: e.target.value,
                })
              }
            />
          </div>
        ))}
      </CardContent>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-1">도구 선택</h3>
        <p className="text-sm text-muted-foreground">
          Agent가 사용할 도구를 선택합니다. 여러 도구를 동시에 활성화할 수 있습니다.
          {taskPurpose && (
            <span className="ml-1">
              <Star className="inline h-3.5 w-3.5 text-orange-500 -mt-0.5" /> 표시는 선택한 목적에 맞는 추천 도구입니다.
            </span>
          )}
        </p>
      </div>

      {TOOL_CATEGORIES.map((category) => (
        <div key={category.id} className="space-y-3">
          {/* Category header */}
          <div className="flex items-center gap-2">
            <div className="h-px flex-1 bg-border" />
            <span className="text-sm font-medium text-muted-foreground px-2">
              {category.name}
            </span>
            <div className="h-px flex-1 bg-border" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {category.tools.map((toolInfo) => {
              const Icon = ICON_MAP[toolInfo.icon] || Plug;
              const enabled = isToolEnabled(toolInfo.type);
              const config = getToolConfig(toolInfo.type);
              const recommended = isRecommended(toolInfo.type, taskPurpose);

              return (
                <Card
                  key={toolInfo.type}
                  className={cn(
                    'transition-colors cursor-pointer',
                    enabled
                      ? 'border-primary bg-primary/5'
                      : recommended
                        ? 'border-orange-300 bg-orange-50/30 dark:bg-orange-950/10'
                        : ''
                  )}
                  onClick={() => toggleTool(toolInfo.type)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-3">
                      <Checkbox
                        checked={enabled}
                        onCheckedChange={() => toggleTool(toolInfo.type)}
                        onClick={(e) => e.stopPropagation()}
                      />
                      <Icon className={cn(
                        'h-5 w-5 flex-shrink-0',
                        enabled ? 'text-primary' : 'text-muted-foreground'
                      )} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-sm">{toolInfo.name}</CardTitle>
                          {recommended && (
                            <Badge variant="outline" className="text-[10px] px-1.5 py-0 border-orange-400 text-orange-600 bg-orange-50 dark:bg-orange-950/30">
                              <Star className="h-3 w-3 mr-0.5" />
                              추천
                            </Badge>
                          )}
                        </div>
                        <CardDescription className="text-xs">
                          {toolInfo.description}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  {enabled && toolInfo.requiresConfig && (
                    <div onClick={(e) => e.stopPropagation()}>
                      {renderConfigFields(toolInfo, config)}
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
