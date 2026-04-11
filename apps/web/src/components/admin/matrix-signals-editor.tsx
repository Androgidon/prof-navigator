import { DIMENSIONS } from "@/lib/question-defaults";
import { ProfessionShortListEditor } from "@/components/admin/profession-short-list-editor";

type MatrixSignalsEditorProps = {
  critical_dimensions: string[];
  important_subjects: string[];
  hobby_signals: string[];
  preferred_environments: string[];
  first_steps_template: string[];
  onChange: (patch: {
    critical_dimensions?: string[];
    important_subjects?: string[];
    hobby_signals?: string[];
    preferred_environments?: string[];
    first_steps_template?: string[];
  }) => void;
};

export function MatrixSignalsEditor({
  critical_dimensions,
  important_subjects,
  hobby_signals,
  preferred_environments,
  first_steps_template,
  onChange,
}: MatrixSignalsEditorProps) {
  const toggleCritical = (dim: string) => {
    const has = critical_dimensions.includes(dim);
    onChange({
      critical_dimensions: has ? critical_dimensions.filter((item) => item !== dim) : [...critical_dimensions, dim],
    });
  };

  return (
    <>
      <div className="admin-editor-box">
        <div className="admin-editor-box-title">Critical Dimensions</div>
        <div className="admin-chip-grid">
          {DIMENSIONS.map((dim) => (
            <button
              type="button"
              key={dim}
              className={`admin-chip ${critical_dimensions.includes(dim) ? "admin-chip-active" : ""}`}
              onClick={() => toggleCritical(dim)}
            >
              {dim}
            </button>
          ))}
        </div>
      </div>

      <ProfessionShortListEditor
        label="Important Subjects"
        value={important_subjects}
        onChange={(next) => onChange({ important_subjects: next })}
      />
      <ProfessionShortListEditor
        label="Hobby Signals"
        value={hobby_signals}
        onChange={(next) => onChange({ hobby_signals: next })}
      />
      <ProfessionShortListEditor
        label="Preferred Environments"
        value={preferred_environments}
        onChange={(next) => onChange({ preferred_environments: next })}
      />
      <ProfessionShortListEditor
        label="First Steps Template"
        value={first_steps_template}
        onChange={(next) => onChange({ first_steps_template: next })}
      />
    </>
  );
}
