import { cn } from "@/lib/utils";

interface FactCardProps {
  label: string;
  value: string;
  icon?: string;
  className?: string;
}

export function FactCard({ label, value, icon, className }: FactCardProps) {
  return (
    <div className={cn("fact-card", className)}>
      {icon && <span className="fact-icon">{icon}</span>}
      <p className="fact-label">{label}</p>
      <p className="fact-value">{value}</p>
    </div>
  );
}

interface FactsRowProps {
  salary?: string;
  demand?: string;
  education?: string;
  className?: string;
}

export function FactsRow({ salary, demand, education, className }: FactsRowProps) {
  const facts = [
    { label: "Зарплата", value: salary || "Данные по запросу", icon: "💰" },
    { label: "Спрос", value: demand || "Высокий", icon: "📈" },
    { label: "Образование", value: education || "От бакалавриата", icon: "🎓" },
  ];

  return (
    <div className={cn("facts-row", className)}>
      {facts.map((fact) => (
        <FactCard
          key={fact.label}
          label={fact.label}
          value={fact.value}
          icon={fact.icon}
        />
      ))}
    </div>
  );
}