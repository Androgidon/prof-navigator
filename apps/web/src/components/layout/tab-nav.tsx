import { cn } from "@/lib/utils";

type TabId = "profile" | "results" | "favorites" | "settings";

interface Tab {
  id: TabId;
  label: string;
}

const tabs: Tab[] = [
  { id: "profile", label: "Профиль" },
  { id: "results", label: "Результаты" },
  { id: "favorites", label: "Избранное" },
  { id: "settings", label: "Настройки" },
];

interface TabNavProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
  className?: string;
}

export function TabNav({ activeTab, onTabChange, className }: TabNavProps) {
  return (
    <nav className={cn("tab-nav", className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          onClick={() => onTabChange(tab.id)}
          className={cn("tab-item", activeTab === tab.id && "tab-item-active")}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}