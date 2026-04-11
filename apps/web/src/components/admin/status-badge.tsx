import { cn } from "@/lib/utils";

export function StatusBadge({ value }: { value: string }) {
  return <span className={cn("admin-status-badge", `admin-status-${value}`)}>{value}</span>;
}
