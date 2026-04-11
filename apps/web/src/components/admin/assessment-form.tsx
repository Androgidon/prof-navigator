"use client";

import { useEffect, useState } from "react";
import { DirtyIndicator } from "@/components/admin/dirty-indicator";
import { FormFeedback } from "@/components/admin/form-feedback";
import { useDirtyFormState } from "@/hooks/use-dirty-form-state";
import { useUnsavedChangesGuard } from "@/hooks/use-unsaved-changes-guard";

type Assessment = {
  slug: string;
  title: string;
  description: string | null;
  target_items_count: number;
  min_items_count: number;
  max_items_count: number;
  expected_duration_min: number;
  is_active: boolean;
  version: number;
  scoring_config_json: Record<string, unknown>;
  question_mix_config_json: Record<string, unknown>;
};

type AssessmentFormProps = {
  value: Assessment;
  loading?: boolean;
  onSave: (next: Partial<Assessment>) => Promise<void>;
  onCloneRequired: () => void;
};

export function AssessmentForm({ value, onSave, onCloneRequired, loading }: AssessmentFormProps) {
  const [form, setForm] = useState<Assessment>(value);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setForm(value);
  }, [value]);

  const dirty = useDirtyFormState(value, form);
  useUnsavedChangesGuard(dirty);

  const invalid =
    !form.title.trim() ||
    form.target_items_count <= 0 ||
    form.min_items_count <= 0 ||
    form.max_items_count <= 0 ||
    form.expected_duration_min <= 0;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setSuccess(null);
    setError(null);
    try {
      await onSave({
        title: form.title,
        description: form.description,
        target_items_count: form.target_items_count,
        min_items_count: form.min_items_count,
        max_items_count: form.max_items_count,
        expected_duration_min: form.expected_duration_min,
      });
      setSuccess("Сохранено");
    } catch (err) {
      const e = err as Error & { code?: string };
      if (e.code === "requires_clone") {
        onCloneRequired();
        return;
      }
      setError(e.message || "Ошибка сохранения");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form className="admin-form" onSubmit={handleSubmit}>
      <div className="admin-form-header">
        <h2>{form.slug}</h2>
        <DirtyIndicator dirty={dirty} />
      </div>

      <label className="admin-field">
        <span>Title</span>
        <input
          value={form.title}
          onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
          className="admin-input"
        />
      </label>

      <label className="admin-field">
        <span>Description</span>
        <textarea
          value={form.description ?? ""}
          onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
          className="admin-textarea"
        />
      </label>

      <div className="admin-grid-two">
        <label className="admin-field">
          <span>Target Items</span>
          <input
            type="number"
            value={form.target_items_count}
            onChange={(e) => setForm((prev) => ({ ...prev, target_items_count: Number(e.target.value) }))}
            className="admin-input"
          />
        </label>

        <label className="admin-field">
          <span>Duration (min)</span>
          <input
            type="number"
            value={form.expected_duration_min}
            onChange={(e) => setForm((prev) => ({ ...prev, expected_duration_min: Number(e.target.value) }))}
            className="admin-input"
          />
        </label>
      </div>

      <div className="admin-grid-two">
        <label className="admin-field">
          <span>Min Items</span>
          <input
            type="number"
            value={form.min_items_count}
            onChange={(e) => setForm((prev) => ({ ...prev, min_items_count: Number(e.target.value) }))}
            className="admin-input"
          />
        </label>

        <label className="admin-field">
          <span>Max Items</span>
          <input
            type="number"
            value={form.max_items_count}
            onChange={(e) => setForm((prev) => ({ ...prev, max_items_count: Number(e.target.value) }))}
            className="admin-input"
          />
        </label>
      </div>

      <div className="admin-meta-box">
        <p>Version: {form.version}</p>
        <p>Status: {form.is_active ? "active" : "draft"}</p>
        <p>Matrix Version: {String(form.question_mix_config_json?.matrix_version_slug ?? "—")}</p>
      </div>

      <div className="admin-form-actions">
        <button type="submit" className="admin-btn admin-btn-primary" disabled={saving || loading || !dirty || invalid}>
          {saving ? "Сохранение..." : "Сохранить"}
        </button>
      </div>

      <FormFeedback success={success} error={error} />
    </form>
  );
}
