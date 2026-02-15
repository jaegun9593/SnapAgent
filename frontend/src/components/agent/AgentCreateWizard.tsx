import { useState } from 'react';
import { useAgents } from '@/hooks/useAgents';
import { PreferenceStep } from './steps/PreferenceStep';
import { BasicInfoStep } from './steps/BasicInfoStep';
import { FileUploadStep } from './steps/FileUploadStep';
import { ToolSelectStep } from './steps/ToolSelectStep';
import { ModelSelectStep } from './steps/ModelSelectStep';
import { TestStep } from './steps/TestStep';
import { WizardLayout } from './wizard/WizardLayout';
import type { Step } from './wizard/StepIndicator';
import type { AgentCreate, AgentToolConfig, AgentPreferences } from '@/types';
import { agentService } from '@/services/agentService';
import { generateSystemPrompt } from '@/lib/generateSystemPrompt';

interface AgentCreateWizardProps {
  onComplete: (agentId: string) => void;
  onCancel: () => void;
}

const STEPS: Step[] = [
  { id: 1, name: '선호 설정', description: '목적, 형식, 톤 설정' },
  { id: 2, name: '기본 정보', description: '이름, 설명, 시스템 프롬프트' },
  { id: 3, name: '도구 선택', description: '사용할 도구 설정' },
  { id: 4, name: '파일 업로드', description: 'RAG용 문서 업로드' },
  { id: 5, name: '모델 선택', description: 'LLM 및 임베딩 모델' },
  { id: 6, name: '테스트', description: 'Agent 테스트' },
];

export function AgentCreateWizard({ onComplete, onCancel }: AgentCreateWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [preferences, setPreferences] = useState<AgentPreferences>({
    task_purpose: '',
    response_format: '',
    response_tone: '',
  });
  const [agentData, setAgentData] = useState<Partial<AgentCreate>>({
    name: '',
    description: '',
    system_prompt: '',
    status: 'draft',
  });
  const [fileIds, setFileIds] = useState<string[]>([]);
  const [tools, setTools] = useState<AgentToolConfig[]>([]);
  const [createdAgentId, setCreatedAgentId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const { createAgentAsync, isCreating } = useAgents();

  const handleNext = async () => {
    if (currentStep === 1) {
      // Validate preferences: all 3 must be selected
      if (!preferences.task_purpose || !preferences.response_format || !preferences.response_tone) {
        return;
      }
      // Auto-generate system prompt from preferences
      const generated = generateSystemPrompt(preferences);
      if (generated) {
        setAgentData((prev) => ({ ...prev, system_prompt: generated }));
      }
    }

    if (currentStep === 5) {
      // Create agent before test step
      try {
        setIsProcessing(true);

        const agent = await createAgentAsync({
          name: agentData.name || 'New Agent',
          description: agentData.description,
          system_prompt: agentData.system_prompt,
          template_id: agentData.template_id,
          model_id: agentData.model_id,
          embedding_model_id: agentData.embedding_model_id,
          config: { ...((agentData.config as Record<string, unknown>) || {}), preferences },
          tools: tools.length > 0 ? tools : undefined,
          file_ids: fileIds.length > 0 ? fileIds : undefined,
          sub_agent_ids: agentData.sub_agent_ids,
          status: 'configured',
        });
        setCreatedAgentId(agent.id);

        // RAG 파일이 있으면 자동으로 임베딩 처리 실행
        if (fileIds.length > 0) {
          try {
            await agentService.process(agent.id, { force: true });
          } catch (processErr) {
            console.error('File processing failed:', processErr);
          }
        }

        setCompletedSteps((prev) =>
          prev.includes(currentStep) ? prev : [...prev, currentStep]
        );
        setCurrentStep(currentStep + 1);
      } catch (err) {
        console.error('Failed to create agent:', err);
      } finally {
        setIsProcessing(false);
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

  const isNextDisabled = () => {
    if (isCreating || isProcessing) return true;
    if (currentStep === 1) {
      return !preferences.task_purpose || !preferences.response_format || !preferences.response_tone;
    }
    return false;
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
      isNextDisabled={isNextDisabled()}
      isFinishing={isCreating || isProcessing}
    >
      {currentStep === 1 && (
        <PreferenceStep
          preferences={preferences}
          onChange={setPreferences}
        />
      )}
      {currentStep === 2 && (
        <BasicInfoStep
          data={agentData}
          onChange={(data) => setAgentData({ ...agentData, ...data })}
          preferences={preferences}
        />
      )}
      {currentStep === 3 && (
        <ToolSelectStep
          tools={tools}
          onChange={setTools}
          taskPurpose={preferences.task_purpose}
        />
      )}
      {currentStep === 4 && (
        <FileUploadStep
          fileIds={fileIds}
          onChange={setFileIds}
        />
      )}
      {currentStep === 5 && (
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
      {currentStep === 6 && createdAgentId && (
        <TestStep agentId={createdAgentId} />
      )}
    </WizardLayout>
  );
}
