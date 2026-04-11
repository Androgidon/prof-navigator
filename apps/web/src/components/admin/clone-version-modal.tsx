type CloneVersionModalProps = {
  open: boolean;
  title: string;
  description: string;
  loading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
};

export function CloneVersionModal({
  open,
  title,
  description,
  loading,
  onConfirm,
  onCancel,
}: CloneVersionModalProps) {
  if (!open) {
    return null;
  }

  return (
    <div className="admin-modal-overlay" role="dialog" aria-modal="true">
      <div className="admin-modal">
        <h3>{title}</h3>
        <p>{description}</p>
        <div className="admin-modal-actions">
          <button type="button" className="admin-btn admin-btn-ghost" onClick={onCancel} disabled={loading}>
            Отмена
          </button>
          <button type="button" className="admin-btn admin-btn-primary" onClick={onConfirm} disabled={loading}>
            {loading ? "Клонирование..." : "Создать draft-клон"}
          </button>
        </div>
      </div>
    </div>
  );
}
