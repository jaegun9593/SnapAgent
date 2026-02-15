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
import type { Agent, AgentUpdate, AgentToolConfig, AgentPreferences } from '@/types';
import { agentService } from '@/services/agentService';
import { generateSystemPrompt } from '@/lib/generateSystemPrompt';

interface AgentEditWizardProps {
  agent: Agent;
  onComplete: () => void;
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

function hydratePreferences(config?: Record<string, unknown>): AgentPreferences {
  const prefs = config?.preferences as AgentPreferences | undefined;
  return {
    task_purpose: prefs?.task_purpose || '',
    response_format: prefs?.response_format || '',
    response_tone: prefs?.response_tone || '',
  };
}

function hydrateTools(agent: Agent): AgentToolConfig[] {
  if (!agent.tools || agent.tools.length === 0) return [];
  return agent.tools.map((t) => ({
    tool_type: t.tool_type as AgentToolConfig['tool_type'],
    tool_config: t.tool_config,
    is_enabled: t.is_enabled,
    sort_order: t.sort_order,
  }));
}

export function AgentEditWizard({ agent, onComplete, onCancel }: AgentEditWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [preferences, setPreferences] = useState<AgentPreferences>(
    hydratePreferences(agent.config)
  );
  const [agentData, setAgentData] = useState<Partial<AgentUpdate>>({
    name: agent.name,
    description: agent.description || '',
    system_prompt: agent.system_prompt || '',
    template_id: agent.template_id,
    model_id: agent.model_id,
    embedding_model_id: agent.embedding_model_id,
    config: agent.config,
    status: agent.status,
  });
  const [fileIds, setFileIds] = useState<string[]>(agent.file_ids || []);
  const [tools, setTools] = useState<AgentToolConfig[]>(hydrateTools(agent));
  const [isProcessing, setIsProcessing] = useState(false);
  const [isUpdated, setIsUpdated] = useState(false);
  const { updateAgentAsync, isUpdating } = useAgents();

  const initialFileIds = agent.file_ids || [];

  const handleNext = async () => {
    if (currentStep === 1) {
      if (!preferences.task_purpose || !preferences.response_format || !preferences.response_tone) {
        return;
      }
      const generated = generateSystemPrompt(preferences);
      if (generated) {
        setAgentData((prev) => ({ ...prev, system_prompt: generated }));
      }
    }

    if (currentStep === 5) {
      // Update agent before test step
      try {
        setIsProcessing(true);

        await updateAgentAsync({
          id: agent.id,
          data: {
            name: agentData.name || agent.name,
            description: agentData.description,
            system_prompt: agentData.system_prompt,
            template_id: agentData.template_id,
            model_id: agentData.model_id,
            embedding_model_id: agentData.embedding_model_id,
            config: { ...((agentData.config as Record<string, unknown>) || {}), preferences },
            tools: tools.length > 0 ? tools : undefined,
            file_ids: fileIds.length > 0 ? fileIds : undefined,
            sub_agent_ids: agentData.sub_agent_ids as string[] | undefined,
            status: 'configured',
          },
        });

        // 파일이 변경되었으면 재임베딩
        const filesChanged =
          JSON.stringify([...fileIds].sort()) !== JSON.stringify([...initialFileIds].sort());
        if (fileIds.length > 0 && filesChanged) {
          try {
            await agentService.process(agent.id, { force: true });
          } catch (processErr) {
            console.error('File processing failed:', processErr);
          }
        }

        setIsUpdated(true);
        setCompletedSteps((prev) =>
          prev.includes(currentStep) ? prev : [...prev, currentStep]
        );
        setCurrentStep(currentStep + 1);
      } catch (err) {
        console.error('Failed to update agent:', err);
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
    onComplete();
  };

  const isNextDisabled = () => {
    if (isUpdating || isProcessing) return true;
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
      isFinishing={isUpdating || isProcessing}
      finishButtonText="완료"
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
      {currentStep === 6 && (
        <TestStep agentId={agent.id} />
      )}
    </WizardLayout>
  );
}
