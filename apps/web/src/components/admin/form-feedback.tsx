type FormFeedbackProps = {
  success: string | null;
  error: string | null;
};

export function FormFeedback({ success, error }: FormFeedbackProps) {
  return (
    <>
      {success && <div className="admin-success">{success}</div>}
      {error && <div className="admin-error">{error}</div>}
    </>
  );
}
