import { DIMENSIONS } from "@/lib/question-defaults";

type MatrixDimensionEditorProps = {
  targets: Record<string, number>;
  weights: Record<string, number>;
  onTargetsChange: (next: Record<string, number>) => void;
  onWeightsChange: (next: Record<string, number>) => void;
};

export function MatrixDimensionEditor({ targets, weights, onTargetsChange, onWeightsChange }: MatrixDimensionEditorProps) {
  return (
    <div className="admin-editor-box">
      <div className="admin-editor-box-title">Dimension Model</div>
      <div className="admin-grid-two">
        {DIMENSIONS.map((dim) => (
          <div key={dim} className="admin-grid-two">
            <label className="admin-field">
              <span>{dim} target</span>
              <input
                className="admin-input"
                type="number"
                min={0}
                max={100}
                value={targets[dim] ?? 50}
                onChange={(e) => onTargetsChange({ ...targets, [dim]: Number(e.target.value) })}
              />
            </label>
            <label className="admin-field">
              <span>{dim} weight</span>
              <input
                className="admin-input"
                type="number"
                step="0.1"
                min={0}
                value={weights[dim] ?? 1}
                onChange={(e) => onWeightsChange({ ...weights, [dim]: Number(e.target.value) })}
              />
            </label>
          </div>
        ))}
      </div>
    </div>
  );
}
