import { cn } from "@/lib/utils";

interface ActionItemProps {
  step: number;
  title: string;
  description?: string;
  className?: string;
}

export function ActionItem({ step, title, description, className }: ActionItemProps) {
  return (
    <div className={cn("action-item", className)}>
      <div className="action-step">
        <span className="action-number">{step}</span>
      </div>
      <div className="action-content">
        <h4 className="action-title">{title}</h4>
        {description && <p className="action-description">{description}</p>}
      </div>
    </div>
  );
}

interface ActionListProps {
  title?: string;
  items: { title: string; description?: string }[];
  className?: string;
}

export function ActionList({ title = "Что можно начать уже сейчас", items, className }: ActionListProps) {
  return (
    <div className={cn("action-list", className)}>
      <h3 className="action-list-title">{title}</h3>
      <div className="action-items">
        {items.map((item, index) => (
          <ActionItem
            key={index}
            step={index + 1}
            title={item.title}
            description={item.description}
          />
        ))}
      </div>
    </div>
  );
}