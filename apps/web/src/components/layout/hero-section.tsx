import { type ReactNode } from "react";
import { cn } from "@/lib/utils";

interface HeroSectionProps {
  badge?: ReactNode;
  badgeClassName?: string;
  title: ReactNode;
  titleAccent?: ReactNode;
  subtitle?: ReactNode;
  children?: ReactNode;
  className?: string;
}

export function HeroSection({
  badge,
  badgeClassName,
  title,
  titleAccent,
  subtitle,
  children,
  className,
}: HeroSectionProps) {
  return (
    <section className={cn("hero-section", className)}>
      {badge && (
        <div className={cn("hero-badge", badgeClassName)}>
          {badge}
        </div>
      )}
      <div className="hero-top">
        <h1>
          {title}
          {titleAccent && (
            <>
              {" "}
              <span className="hero-accent">{titleAccent}</span>
            </>
          )}
        </h1>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {children}
    </section>
  );
}