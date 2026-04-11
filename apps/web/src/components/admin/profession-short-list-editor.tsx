type ProfessionShortListEditorProps = {
  label: string;
  value: string[];
  onChange: (next: string[]) => void;
};

export function ProfessionShortListEditor({ label, value, onChange }: ProfessionShortListEditorProps) {
  const update = (index: number, nextValue: string) => {
    const next = [...value];
    next[index] = nextValue;
    onChange(next);
  };

  const add = () => onChange([...value, ""]);
  const remove = (index: number) => onChange(value.filter((_, i) => i !== index));

  return (
    <div className="admin-editor-box">
      <div className="admin-editor-box-title">{label}</div>
      {value.map((item, index) => (
        <div key={`${label}-${index}`} className="admin-option-row">
          <input className="admin-input" value={item} onChange={(e) => update(index, e.target.value)} />
          <button className="admin-btn admin-btn-ghost" type="button" onClick={() => remove(index)}>
            Удалить
          </button>
        </div>
      ))}
      <button className="admin-btn admin-btn-ghost" type="button" onClick={add}>
        Добавить
      </button>
    </div>
  );
}
