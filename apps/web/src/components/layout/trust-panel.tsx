import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface TrustPanelProps {
  title: ReactNode;
  description?: ReactNode;
  items?: ReactNode[];
  children?: ReactNode;
  className?: string;
}

export function TrustPanel({
  title,
  description,
  items,
  children,
  className,
}: TrustPanelProps) {
  return (
    <section className={cn("trust-section", className)}>
      <div className="trust-inner">
        <h2>{title}</h2>
        {description && <p>{description}</p>}
        {items && (
          <div className="benefit-list">
            {items.map((item, index) => (
              <span key={index}>
                <span aria-hidden className="dot" />
                {item}
              </span>
            ))}
          </div>
        )}
        {children}
      </div>
    </section>
  );
}