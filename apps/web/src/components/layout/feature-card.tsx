import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface FeatureCardProps {
  icon?: ReactNode;
  iconBgClassName?: string;
  title: ReactNode;
  description?: ReactNode;
  children?: ReactNode;
  className?: string;
}

export function FeatureCard({
  icon,
  iconBgClassName = "feature-icon",
  title,
  description,
  children,
  className,
}: FeatureCardProps) {
  return (
    <article className={cn("feature-card", className)}>
      {icon && (
        <div className={cn(iconBgClassName, "feature-icon-default")} aria-hidden>
          {icon}
        </div>
      )}
      <h3>{title}</h3>
      {description && <p>{description}</p>}
      {children}
    </article>
  );
}