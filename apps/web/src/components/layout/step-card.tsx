import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface StepCardProps {
  number: number;
  title: ReactNode;
  description?: ReactNode;
  children?: ReactNode;
  className?: string;
}

export function StepCard({
  number,
  title,
  description,
  children,
  className,
}: StepCardProps) {
  return (
    <div className={cn("step-card", className)}>
      <div className="step-marker">
        <span className="step-number">{number}</span>
      </div>
      <div className="step-content">
        {children}
        <div className="step-text">
          <h3>{title}</h3>
          {description && <p>{description}</p>}
        </div>
      </div>
    </div>
  );
}