import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface AnswerOptionRowProps {
  children: ReactNode;
  selected?: boolean;
  onClick?: () => void;
  className?: string;
}

export function AnswerOptionRow({
  children,
  selected,
  onClick,
  className,
}: AnswerOptionRowProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "answer-option-row",
        selected && "answer-option-row-selected",
        className
      )}
    >
      {children}
    </button>
  );
}