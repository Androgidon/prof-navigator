import { DIMENSIONS } from "@/lib/question-defaults";

type DimensionWeightsEditorProps = {
  value: Record<string, number>;
  onChange: (next: Record<string, number>) => void;
};

export function DimensionWeightsEditor({ value, onChange }: DimensionWeightsEditorProps) {
  return (
    <div className="admin-editor-box">
      <div className="admin-editor-box-title">Dimension Weights</div>
      <div className="admin-grid-two">
        {DIMENSIONS.map((dim) => (
          <label key={dim} className="admin-field">
            <span>{dim}</span>
            <input
              className="admin-input"
              type="number"
              step="0.1"
              value={value[dim] ?? ""}
              onChange={(e) => {
                const raw = e.target.value;
                const next = { ...value };
                if (raw === "") {
                  delete next[dim];
                } else {
                  next[dim] = Number(raw);
                }
                onChange(next);
              }}
            />
          </label>
        ))}
      </div>
    </div>
  );
}
