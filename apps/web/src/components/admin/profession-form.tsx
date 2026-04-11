"use client";

import { useState } from "react";
import { DirtyIndicator } from "@/components/admin/dirty-indicator";
import { FormFeedback } from "@/components/admin/form-feedback";
import { ProfessionShortListEditor } from "@/components/admin/profession-short-list-editor";
import { useDirtyFormState } from "@/hooks/use-dirty-form-state";
import { useUnsavedChangesGuard } from "@/hooks/use-unsaved-changes-guard";

export type ProfessionFormState = {
  external_id: number;
  slug: string;
  title: string;
  cluster: string;
  summary: string;
  status: string;
  matrix_version_slug: string;
  first_steps_short: string[];
  important_subjects_short: string[];
};

type ProfessionFormProps = {
  mode: "create" | "edit";
  initialValue: ProfessionFormState;
  onSave: (payload: ProfessionFormState) => Promise<void>;
};

export function ProfessionForm({ mode, initialValue, onSave }: ProfessionFormProps) {
  const [form, setForm] = useState(initialValue);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const dirty = useDirtyFormState(initialValue, form);
  useUnsavedChangesGuard(dirty);

  const invalid = !form.slug.trim() || !form.title.trim() || !form.cluster.trim() || !form.summary.trim();

  return (
    <form
      className="admin-form"
      onSubmit={async (event) => {
        event.preventDefault();
        setSaving(true);
        setSuccess(null);
        setError(null);
        try {
          await onSave(form);
          setSuccess("Сохранено");
        } catch (err) {
          setError(err instanceof Error ? err.message : "Ошибка сохранения");
        } finally {
          setSaving(false);
        }
      }}
    >
      <div className="admin-form-header">
        <h2>{mode === "create" ? "Новая профессия" : form.slug}</h2>
        <DirtyIndicator dirty={dirty} />
      </div>

      <div className="admin-grid-two">
        <label className="admin-field">
          <span>External ID</span>
          <input
            type="number"
            className="admin-input"
            value={form.external_id}
            onChange={(e) => setForm((prev) => ({ ...prev, external_id: Number(e.target.value) }))}
            disabled={mode === "edit"}
          />
        </label>
        <label className="admin-field">
          <span>Slug</span>
          <input className="admin-input" value={form.slug} onChange={(e) => setForm((prev) => ({ ...prev, slug: e.target.value }))} disabled={mode === "edit"} />
        </label>
      </div>

      <div className="admin-grid-two">
        <label className="admin-field">
          <span>Title</span>
          <input className="admin-input" value={form.title} onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))} />
        </label>
        <label className="admin-field">
          <span>Cluster</span>
          <input className="admin-input" value={form.cluster} onChange={(e) => setForm((prev) => ({ ...prev, cluster: e.target.value }))} />
        </label>
      </div>

      <label className="admin-field">
        <span>Summary</span>
        <textarea className="admin-textarea" rows={3} value={form.summary} onChange={(e) => setForm((prev) => ({ ...prev, summary: e.target.value }))} />
      </label>

      <div className="admin-grid-two">
        <label className="admin-field">
          <span>Status</span>
          <select className="admin-input" value={form.status} onChange={(e) => setForm((prev) => ({ ...prev, status: e.target.value }))}>
            <option value="draft">draft</option>
            <option value="active">active</option>
            <option value="archive">archive</option>
          </select>
        </label>
        <label className="admin-field">
          <span>Matrix Version</span>
          <input className="admin-input" value={form.matrix_version_slug} onChange={(e) => setForm((prev) => ({ ...prev, matrix_version_slug: e.target.value }))} />
        </label>
      </div>

      <ProfessionShortListEditor
        label="First Steps (short)"
        value={form.first_steps_short}
        onChange={(next) => setForm((prev) => ({ ...prev, first_steps_short: next }))}
      />

      <ProfessionShortListEditor
        label="Important Subjects (short)"
        value={form.important_subjects_short}
        onChange={(next) => setForm((prev) => ({ ...prev, important_subjects_short: next }))}
      />

      <div className="admin-form-actions">
        <button className="admin-btn admin-btn-primary" type="submit" disabled={saving || invalid || !dirty}>
          {saving ? "Сохранение..." : "Сохранить"}
        </button>
      </div>

      <FormFeedback success={success} error={error} />
    </form>
  );
}
