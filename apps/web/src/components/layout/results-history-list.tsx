type ResultHistoryItem = {
  result_id: string;
  assessment_slug: string;
  test_title: string;
  completed_at: string;
  top_professions: string[];
  is_latest: boolean;
};

type ResultsHistoryListProps = {
  items: ResultHistoryItem[];
  selectedResultId: string | null;
  onSelect: (resultId: string) => void;
};

function formatDateTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Дата недоступна";
  }
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function ResultsHistoryList({ items, selectedResultId, onSelect }: ResultsHistoryListProps) {
  return (
    <div className="settings-card">
      <h2 className="dashboard-section-heading">История прохождений</h2>
      <div className="admin-nav" style={{ gap: "0.5rem", marginTop: "0.75rem" }}>
        {items.map((item) => {
          const selected = item.result_id === selectedResultId;
          const top = item.top_professions.length > 0 ? item.top_professions.slice(0, 3).join(", ") : "Нет рекомендаций";
          return (
            <button
              key={item.result_id}
              type="button"
              onClick={() => onSelect(item.result_id)}
              className={`admin-nav-link ${selected ? "admin-nav-link-active" : ""}`}
              style={{ textAlign: "left" }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", gap: "0.75rem" }}>
                <strong>{formatDateTime(item.completed_at)}</strong>
                {item.is_latest && <span className="admin-status-badge admin-status-draft">Последний</span>}
              </div>
              <div className="admin-help">{item.test_title}</div>
              <div className="admin-help">Топ: {top}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
