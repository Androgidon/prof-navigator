type OptionItem = {
  key: string;
  label: string;
  weights_by_dimension?: Record<string, number>;
};

type OptionsEditorProps = {
  value: OptionItem[];
  onChange: (next: OptionItem[]) => void;
  readOnly?: boolean;
};

export function OptionsEditor({ value, onChange, readOnly }: OptionsEditorProps) {
  const update = (index: number, patch: Partial<OptionItem>) => {
    const next = [...value];
    next[index] = { ...next[index], ...patch };
    onChange(next);
  };

  const add = () => {
    onChange([...value, { key: `${value.length + 1}`, label: "" }]);
  };

  const remove = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  return (
    <div className="admin-editor-box">
      <div className="admin-editor-box-title">Options</div>
      {value.map((opt, index) => (
        <div key={`${opt.key}-${index}`} className="admin-option-row">
          <input
            className="admin-input"
            placeholder="key"
            value={opt.key}
            disabled={readOnly}
            onChange={(e) => update(index, { key: e.target.value })}
          />
          <input
            className="admin-input"
            placeholder="label"
            value={opt.label}
            disabled={readOnly}
            onChange={(e) => update(index, { label: e.target.value })}
          />
          {!readOnly && (
            <button type="button" className="admin-btn admin-btn-ghost" onClick={() => remove(index)}>
              Удалить
            </button>
          )}
        </div>
      ))}
      {!readOnly && (
        <button type="button" className="admin-btn admin-btn-ghost" onClick={add}>
          Добавить option
        </button>
      )}
    </div>
  );
}
