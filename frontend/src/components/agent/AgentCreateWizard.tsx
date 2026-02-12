import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { useAgents } from '@/hooks/useAgents';
import { BasicInfoStep } from './steps/BasicInfoStep';
import { FileUploadStep } from './steps/FileUploadStep';
import { ToolSelectStep } from './steps/ToolSelectStep';
import { ModelSelectStep } from './steps/ModelSelectStep';
import { TestStep } from './steps/TestStep';
import type { AgentCreate, AgentToolConfig } from '@/types';

interface AgentCreateWizardProps {
  onComplete: (agentId: string) => void;
  onCancel: () => void;
}

const STEPS = [
  { id: 'basic', title: '기본 정보', description: '이름, 설명, 시스템 프롬프트' },
  { id: 'files', title: '파일 업로드', description: 'RAG용 문서 업로드' },
  { id: 'tools', title: '도구 선택', description: '사용할 도구 설정' },
  { id: 'model', title: '모델 선택', description: 'LLM 및 임베딩 모델' },
  { id: 'test', title: '테스트', description: 'Agent 테스트' },
];

export function AgentCreateWizard({ onComplete, onCancel }: AgentCreateWizardProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [agentData, setAgentData] = useState<Partial<AgentCreate>>({
    name: '',
    description: '',
    system_prompt: '',
    status: 'draft',
  });
  const [fileIds, setFileIds] = useState<string[]>([]);
  const [tools, setTools] = useState<AgentToolConfig[]>([]);
  const [createdAgentId, setCreatedAgentId] = useState<string | null>(null);
  const { createAgentAsync, isCreating } = useAgents();

  const progress = ((currentStep + 1) / STEPS.length) * 100;

  const handleNext = async () => {
    if (currentStep === STEPS.length - 2) {
      // Create agent before test step
      try {
        const agent = await createAgentAsync({
          name: agentData.name || 'New Agent',
          description: agentData.description,
          system_prompt: agentData.system_prompt,
          template_id: agentData.template_id,
          model_id: agentData.model_id,
          embedding_model_id: agentData.embedding_model_id,
          tools: tools.length > 0 ? tools : undefined,
          file_ids: fileIds.length > 0 ? fileIds : undefined,
          sub_agent_ids: agentData.sub_agent_ids,
          status: 'configured',
        });
        setCreatedAgentId(agent.id);
        setCurrentStep(currentStep + 1);
      } catch (err) {
        console.error('Failed to create agent:', err);
      }
    } else if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    if (createdAgentId) {
      onComplete(createdAgentId);
    }
  };

  return (
    <div className="space-y-6">
      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          {STEPS.map((step, idx) => (
            <span
              key={step.id}
              className={
                idx <= currentStep
                  ? 'text-primary font-medium'
                  : 'text-muted-foreground'
              }
            >
              {step.title}
            </span>
          ))}
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {/* Step Content */}
      <Card>
        <CardContent className="pt-6">
          {currentStep === 0 && (
            <BasicInfoStep
              data={agentData}
              onChange={(data) => setAgentData({ ...agentData, ...data })}
            />
          )}
          {currentStep === 1 && (
            <FileUploadStep
              fileIds={fileIds}
              onChange={setFileIds}
            />
          )}
          {currentStep === 2 && (
            <ToolSelectStep
              tools={tools}
              onChange={setTools}
            />
          )}
          {currentStep === 3 && (
            <ModelSelectStep
              modelId={agentData.model_id}
              embeddingModelId={agentData.embedding_model_id}
              onChange={(modelId, embeddingModelId) =>
                setAgentData({
                  ...agentData,
                  model_id: modelId,
                  embedding_model_id: embeddingModelId,
                })
              }
            />
          )}
          {currentStep === 4 && createdAgentId && (
            <TestStep agentId={createdAgentId} />
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between">
        <div>
          {currentStep > 0 && (
            <Button variant="outline" onClick={handleBack}>
              이전
            </Button>
          )}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onCancel}>
            취소
          </Button>
          {currentStep < STEPS.length - 1 ? (
            <Button onClick={handleNext} disabled={isCreating}>
              {isCreating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  생성 중...
                </>
              ) : (
                '다음'
              )}
            </Button>
          ) : (
            <Button onClick={handleComplete}>완료</Button>
          )}
        </div>
      </div>
    </div>
  );
}
