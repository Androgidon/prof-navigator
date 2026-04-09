import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface SectionContainerProps {
  children: ReactNode;
  className?: string;
  size?: "default" | "narrow" | "wide";
}

const sizeClasses = {
  default: "max-w-5xl",
  narrow: "max-w-3xl",
  wide: "max-w-7xl",
};

export function SectionContainer({
  children,
  className,
  size = "default",
}: SectionContainerProps) {
  return (
    <div className={cn("section-container", sizeClasses[size], className)}>
      {children}
    </div>
  );
}