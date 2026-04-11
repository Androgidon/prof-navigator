import { DIMENSIONS } from "@/lib/question-defaults";

type SliderDimensionGridProps = {
  value: Record<string, number>;
  onChange: (next: Record<string, number>) => void;
};

export function SliderDimensionGrid({ value, onChange }: SliderDimensionGridProps) {
  return (
    <div className="admin-editor-box">
      <div className="admin-editor-box-title">Synthetic Profile</div>
      <div className="admin-grid-two">
        {DIMENSIONS.map((dim) => (
          <label key={dim} className="admin-field">
            <span>{dim}: {value[dim] ?? 50}</span>
            <input
              type="range"
              min={0}
              max={100}
              value={value[dim] ?? 50}
              onChange={(e) => onChange({ ...value, [dim]: Number(e.target.value) })}
            />
          </label>
        ))}
      </div>
    </div>
  );
}
