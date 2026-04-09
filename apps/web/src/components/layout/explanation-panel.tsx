import { cn } from "@/lib/utils";

interface ExplanationItemProps {
  icon?: string;
  title: string;
  score?: number;
  description: string;
  className?: string;
}

export function ExplanationItem({
  icon,
  title,
  score,
  description,
  className,
}: ExplanationItemProps) {
  return (
    <div className={cn("explanation-item", className)}>
      {icon && <span className="explanation-icon">{icon}</span>}
      <div className="explanation-content">
        <div className="explanation-header">
          <h4 className="explanation-title">{title}</h4>
          {score !== undefined && (
            <span className="explanation-score">{score}%</span>
          )}
        </div>
        <p className="explanation-description">{description}</p>
      </div>
    </div>
  );
}

interface ExplanationPanelProps {
  title?: string;
  description?: string;
  children?: React.ReactNode;
  className?: string;
}

export function ExplanationPanel({
  title = "Почему эти профессии?",
  description,
  children,
  className,
}: ExplanationPanelProps) {
  return (
    <div className={cn("explanation-panel", className)}>
      <div className="explanation-panel-header">
        <h3 className="explanation-panel-title">{title}</h3>
        {description && (
          <p className="explanation-panel-description">{description}</p>
        )}
      </div>
      {children ? (
        <div className="explanation-items">{children}</div>
      ) : (
        <div className="explanation-items">
          <ExplanationItem
            icon="🧠"
            title="Психологический профиль"
            score={85}
            description="Ваш профиль показывает склонность к аналитическому мышлению и решению сложных задач."
          />
          <ExplanationItem
            icon="📚"
            title="Сильные предметы"
            score={72}
            description="Математика и физика — ваши сильные стороны, что важно для технических профессий."
          />
          <ExplanationItem
            icon="🎯"
            title="Интересы"
            score={68}
            description="Ваши заявленные интересы в IT и технологиях совпадают с требованиями профессий."
          />
          <ExplanationItem
            icon="📍"
            title="Региональный спрос"
            score={55}
            description="В вашем регионе есть спрос на специалистов в технологической сфере."
          />
        </div>
      )}
    </div>
  );
}