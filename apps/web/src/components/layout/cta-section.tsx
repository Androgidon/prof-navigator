import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface CTASectionProps {
  title: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
  actions?: ReactNode;
  className?: string;
}

export function CTASection({
  title,
  description,
  action,
  actions,
  className,
}: CTASectionProps) {
  return (
    <section className={cn("cta-section", className)}>
      <div className="cta-content">
        <h2>{title}</h2>
        {description && <p>{description}</p>}
        {actions ? (
          <div className="cta-actions">{actions}</div>
        ) : action ? (
          <div className="cta-actions">{action}</div>
        ) : null}
      </div>
    </section>
  );
}