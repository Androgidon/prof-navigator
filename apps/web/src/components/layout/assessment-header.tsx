import { cn } from "@/lib/utils";

interface AssessmentHeaderProps {
  sectionLabel: string;
  currentStep: number;
  totalSteps: number;
  className?: string;
}

export function AssessmentHeader({
  sectionLabel,
  currentStep,
  totalSteps,
  className,
}: AssessmentHeaderProps) {
  return (
    <div className={cn("assessment-header", className)}>
      <span className="assessment-section-label">{sectionLabel}</span>
      <span className="assessment-step-counter">
        {currentStep} из {totalSteps}
      </span>
    </div>
  );
}