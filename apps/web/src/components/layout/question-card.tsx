import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface QuestionCardProps {
  children: ReactNode;
  className?: string;
}

export function QuestionCard({ children, className }: QuestionCardProps) {
  return (
    <div className={cn("question-card", className)}>
      {children}
    </div>
  );
}