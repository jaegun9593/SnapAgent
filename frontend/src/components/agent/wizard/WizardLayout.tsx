import { ArrowLeft, ArrowRight, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { StepIndicator, type Step } from './StepIndicator';

interface WizardLayoutProps {
  steps: Step[];
  currentStep: number;
  completedSteps: number[];
  children: React.ReactNode;
  onBack: () => void;
  onNext: () => void;
  onFinish: () => void;
  onCancel: () => void;
  isNextDisabled?: boolean;
  isFinishing?: boolean;
  isBackDisabled?: boolean;
  finishButtonText?: string;
}

export function WizardLayout({
  steps,
  currentStep,
  completedSteps,
  children,
  onBack,
  onNext,
  onFinish,
  onCancel,
  isNextDisabled = false,
  isFinishing = false,
  isBackDisabled = false,
  finishButtonText = '완료',
}: WizardLayoutProps) {
  const isLastStep = currentStep === steps.length;

  return (
    <Card className="w-full">
      <CardHeader className="pb-4">
        <StepIndicator steps={steps} currentStep={currentStep} completedSteps={completedSteps} />
      </CardHeader>
      <CardContent className="min-h-[400px]">{children}</CardContent>
      <CardFooter className="flex justify-between border-t pt-4">
        <div className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={onBack}
            disabled={currentStep === 1 || isBackDisabled}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            이전
          </Button>
        </div>
        <div className="flex gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            취소
          </Button>
          {isLastStep ? (
            <Button type="button" onClick={onFinish} disabled={isNextDisabled || isFinishing}>
              {isFinishing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {finishButtonText} 중...
                </>
              ) : (
                finishButtonText
              )}
            </Button>
          ) : (
            <Button type="button" onClick={onNext} disabled={isNextDisabled}>
              다음
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  );
}
