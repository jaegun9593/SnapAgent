import { useState } from 'react';
import { useAgents } from '@/hooks/useAgents';
import { BasicInfoStep } from './steps/BasicInfoStep';
import { FileUploadStep } from './steps/FileUploadStep';
import { ToolSelectStep } from './steps/ToolSelectStep';
import { ModelSelectStep } from './steps/ModelSelectStep';
import { TestStep } from './steps/TestStep';
import { WizardLayout } from './wizard/WizardLayout';
import type { Step } from './wizard/StepIndicator';
import type { AgentCreate, AgentToolConfig } from '@/types';

interface AgentCreateWizardProps {
  onComplete: (agentId: string) => void;
  onCancel: () => void;
}

const STEPS: Step[] = [
  { id: 1, name: '기본 정보', description: '이름, 설명, 시스템 프롬프트' },
  { id: 2, name: '파일 업로드', description: 'RAG용 문서 업로드' },
  { id: 3, name: '도구 선택', description: '사용할 도구 설정' },
  { id: 4, name: '모델 선택', description: 'LLM 및 임베딩 모델' },
  { id: 5, name: '테스트', description: 'Agent 테스트' },
];

export function AgentCreateWizard({ onComplete, onCancel }: AgentCreateWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
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

  const handleNext = async () => {
    if (currentStep === 4) {
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
        setCompletedSteps((prev) =>
          prev.includes(currentStep) ? prev : [...prev, currentStep]
        );
        setCurrentStep(currentStep + 1);
      } catch (err) {
        console.error('Failed to create agent:', err);
      }
    } else if (currentStep < STEPS.length) {
      setCompletedSteps((prev) =>
        prev.includes(currentStep) ? prev : [...prev, currentStep]
      );
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    if (createdAgentId) {
      onComplete(createdAgentId);
    }
  };

  return (
    <WizardLayout
      steps={STEPS}
      currentStep={currentStep}
      completedSteps={completedSteps}
      onBack={handleBack}
      onNext={handleNext}
      onFinish={handleComplete}
      onCancel={onCancel}
      isNextDisabled={isCreating}
      isFinishing={isCreating}
    >
      {currentStep === 1 && (
        <BasicInfoStep
          data={agentData}
          onChange={(data) => setAgentData({ ...agentData, ...data })}
        />
      )}
      {currentStep === 2 && (
        <FileUploadStep
          fileIds={fileIds}
          onChange={setFileIds}
        />
      )}
      {currentStep === 3 && (
        <ToolSelectStep
          tools={tools}
          onChange={setTools}
        />
      )}
      {currentStep === 4 && (
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
      {currentStep === 5 && createdAgentId && (
        <TestStep agentId={createdAgentId} />
      )}
    </WizardLayout>
  );
}
