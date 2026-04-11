import { cn } from "@/lib/utils";

interface SearchFilterBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  showFilters?: boolean;
}

export function SearchFilterBar({
  value,
  onChange,
  placeholder = "Поиск профессий...",
  className,
  showFilters = true,
}: SearchFilterBarProps) {
  return (
    <div className={cn("search-filter-bar", className)}>
      <div className="search-input-wrapper">
        <svg
          className="search-icon"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>
        <input
          type="search"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="search-input"
        />
      </div>
      {showFilters && (
        <div className="filter-buttons">
          <button type="button" className="filter-btn">
            Все
          </button>
          <button type="button" className="filter-btn">
            Технологии
          </button>
          <button type="button" className="filter-btn">
            Медицина
          </button>
          <button type="button" className="filter-btn">
            Бизнес
          </button>
        </div>
      )}
    </div>
  );
}