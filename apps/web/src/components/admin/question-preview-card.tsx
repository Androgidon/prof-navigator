type QuestionPreviewCardProps = {
  questionType: string;
  text: string;
  options: Array<{ key: string; label: string }>;
};

export function QuestionPreviewCard({ questionType, text, options }: QuestionPreviewCardProps) {
  return (
    <div className="admin-preview-card">
      <h3>UI Preview</h3>
      <p className="admin-preview-text">{text || "Текст вопроса"}</p>
      {questionType === "likert" ? (
        <div className="admin-likert-row">
          {options.map((option) => (
            <button type="button" key={option.key} className="admin-likert-btn">
              {option.key}
            </button>
          ))}
        </div>
      ) : (
        <div className="admin-option-list">
          {options.map((option) => (
            <label key={option.key} className="admin-preview-option">
              <input type={questionType === "multi_select" || questionType === "multi_select_or_ranking" ? "checkbox" : "radio"} readOnly />
              <span>{option.label || option.key}</span>
            </label>
          ))}
        </div>
      )}
    </div>
  );
}
