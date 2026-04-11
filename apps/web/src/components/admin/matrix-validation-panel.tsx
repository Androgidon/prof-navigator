"use client";

type ValidationIssue = {
  severity: string;
  code: string;
  message: string;
};

type MatrixValidationPanelProps = {
  valid: boolean;
  completenessScore: number;
  hardErrors: ValidationIssue[];
  warnings: ValidationIssue[];
};

export function MatrixValidationPanel({ valid, completenessScore, hardErrors, warnings }: MatrixValidationPanelProps) {
  return (
    <div className="admin-editor-box">
      <div className="admin-editor-box-title">Validation</div>
      <p>Completeness: {completenessScore}%</p>
      <p>Status: {valid ? "valid" : "invalid"}</p>

      {hardErrors.length > 0 && (
        <div className="admin-error">
          <strong>Hard errors</strong>
          <ul>
            {hardErrors.map((issue) => (
              <li key={issue.code}>{issue.message}</li>
            ))}
          </ul>
        </div>
      )}

      {warnings.length > 0 && (
        <div className="admin-loading">
          <strong>Warnings</strong>
          <ul>
            {warnings.map((issue) => (
              <li key={issue.code}>{issue.message}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
