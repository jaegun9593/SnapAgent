import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/axios';
import type { ModelListResponse } from '@/types';

interface ModelSelectStepProps {
  modelId?: string;
  embeddingModelId?: string;
  onChange: (modelId?: string, embeddingModelId?: string) => void;
}

export function ModelSelectStep({
  modelId,
  embeddingModelId,
  onChange,
}: ModelSelectStepProps) {
  const { data: modelsData, isLoading } = useQuery({
    queryKey: ['models'],
    queryFn: async () => {
      const response = await api.get<ModelListResponse>('/models/');
      return response.data;
    },
  });

  const models = modelsData?.models || [];
  const llmModels = models.filter((m) => m.model_type === 'llm' && m.is_active);
  const embeddingModels = models.filter(
    (m) => m.model_type === 'embedding' && m.is_active
  );

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-1">모델 선택</h3>
        <p className="text-sm text-muted-foreground">
          Agent가 사용할 LLM 모델과 임베딩 모델을 선택합니다.
        </p>
      </div>

      {isLoading ? (
        <div className="text-center py-8 text-muted-foreground">
          모델 목록 로딩 중...
        </div>
      ) : (
        <div className="space-y-6">
          {/* LLM Model Selection */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">LLM 모델</CardTitle>
              <CardDescription>
                대화 응답을 생성하는 주요 언어 모델을 선택합니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Label>LLM 모델 선택</Label>
                <Select
                  value={modelId || ''}
                  onValueChange={(val) => onChange(val || undefined, embeddingModelId)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="LLM 모델을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    {llmModels.map((model) => (
                      <SelectItem key={model.id} value={model.id}>
                        <div className="flex items-center gap-2">
                          <span>{model.name}</span>
                          <Badge variant="outline" className="text-xs">
                            {model.provider}
                          </Badge>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {llmModels.length === 0 && (
                  <p className="text-xs text-muted-foreground">
                    관리자에게 모델 등록을 요청하세요.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Embedding Model Selection */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">임베딩 모델</CardTitle>
              <CardDescription>
                RAG 도구를 사용할 경우 문서 임베딩에 사용할 모델을 선택합니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Label>임베딩 모델 선택</Label>
                <Select
                  value={embeddingModelId || ''}
                  onValueChange={(val) => onChange(modelId, val || undefined)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="임베딩 모델을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    {embeddingModels.map((model) => (
                      <SelectItem key={model.id} value={model.id}>
                        <div className="flex items-center gap-2">
                          <span>{model.name}</span>
                          <Badge variant="outline" className="text-xs">
                            {model.provider}
                          </Badge>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {embeddingModels.length === 0 && (
                  <p className="text-xs text-muted-foreground">
                    RAG를 사용하지 않으면 선택하지 않아도 됩니다.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
