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
        <div className="trust-shield" aria-hidden>
          <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2l7 3v6c0 5-3.5 9.5-7 11-3.5-1.5-7-6-7-11V5l7-3z" />
            <path d="m9 12 2 2 4-4" />
          </svg>
        </div>
        <h2>{title}</h2>
        {description && <p>{description}</p>}
        {items && (
          <div className="benefit-list">
            {items.map((item, index) => (
              <span key={index}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                  <path d="M20 6 9 17l-5-5" />
                </svg>
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