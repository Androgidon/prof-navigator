import { cn } from "@/lib/utils";

interface ContentPanelProps {
  title: string;
  children?: React.ReactNode;
  className?: string;
}

export function ContentPanel({ title, children, className }: ContentPanelProps) {
  return (
    <div className={cn("content-panel", className)}>
      <h3 className="content-panel-title">{title}</h3>
      {children}
    </div>
  );
}

interface SubjectChipProps {
  name: string;
  importance?: "high" | "medium" | "low";
  className?: string;
}

export function SubjectChip({ name, importance = "medium", className }: SubjectChipProps) {
  return (
    <span className={cn("subject-chip", `subject-chip-${importance}`, className)}>
      {name}
    </span>
  );
}

interface SubjectsListProps {
  subjects: string[];
  className?: string;
}

export function SubjectsList({ subjects, className }: SubjectsListProps) {
  return (
    <div className={cn("subjects-list", className)}>
      {subjects.map((subject) => (
        <SubjectChip key={subject} name={subject} />
      ))}
    </div>
  );
}