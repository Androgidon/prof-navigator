import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface FocusedTaskLayoutProps {
  children: ReactNode;
  className?: string;
}

export function FocusedTaskLayout({ children, className }: FocusedTaskLayoutProps) {
  return (
    <div className={cn("focused-task-layout", className)}>
      {children}
    </div>
  );
}