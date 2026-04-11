type QuestionFilters = {
  assessment_slug: string;
  block: string;
  question_type: string;
  status_filter: string;
  q: string;
};

type QuestionFiltersBarProps = {
  value: QuestionFilters;
  onChange: (next: QuestionFilters) => void;
  onApply: () => void;
};

export function QuestionFiltersBar({ value, onChange, onApply }: QuestionFiltersBarProps) {
  return (
    <div className="admin-filters">
      <input
        className="admin-input"
        placeholder="assessment_slug"
        value={value.assessment_slug}
        onChange={(e) => onChange({ ...value, assessment_slug: e.target.value })}
      />
      <input
        className="admin-input"
        placeholder="block"
        value={value.block}
        onChange={(e) => onChange({ ...value, block: e.target.value })}
      />
      <input
        className="admin-input"
        placeholder="question_type"
        value={value.question_type}
        onChange={(e) => onChange({ ...value, question_type: e.target.value })}
      />
      <input
        className="admin-input"
        placeholder="status"
        value={value.status_filter}
        onChange={(e) => onChange({ ...value, status_filter: e.target.value })}
      />
      <input
        className="admin-input"
        placeholder="search"
        value={value.q}
        onChange={(e) => onChange({ ...value, q: e.target.value })}
      />
      <button className="admin-btn admin-btn-primary" onClick={onApply} type="button">
        Применить
      </button>
    </div>
  );
}
