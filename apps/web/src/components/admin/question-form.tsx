"use client";

import { useMemo, useState } from "react";
import { DirtyIndicator } from "@/components/admin/dirty-indicator";
import { DimensionWeightsEditor } from "@/components/admin/dimension-weights-editor";
import { FormFeedback } from "@/components/admin/form-feedback";
import { OptionsEditor } from "@/components/admin/options-editor";
import { QuestionPreviewCard } from "@/components/admin/question-preview-card";
import { SignalPreviewPanel } from "@/components/admin/signal-preview-panel";
import { useDirtyFormState } from "@/hooks/use-dirty-form-state";
import { useUnsavedChangesGuard } from "@/hooks/use-unsaved-changes-guard";
import { DEFAULT_LIKERT_OPTIONS, DIMENSIONS, QUESTION_TYPES } from "@/lib/question-defaults";

export type QuestionFormState = {
  assessment_version_slug: string;
  question_id: string;
  block: string;
  subblock: string;
  question_type: string;
  text: string;
  primary_dimension: string;
  secondary_dimensions: string[];
  weights_by_dimension_json: Record<string, number>;
  options_json: Array<{ key: string; label: string; weights_by_dimension?: Record<string, number> }>;
  consistency_pair_id: string;
  difficulty: string;
  is_required: boolean;
  active_in_scoring: boolean;
  experiment_tag: string;
  experiment_mode: string;
  boundary_metadata_json: Record<string, unknown> | null;
  order_hint: number;
  status: string;
  question_purpose: string;
  notes: string;
};

type QuestionFormProps = {
  mode: "create" | "edit";
  initialValue: QuestionFormState;
  onSave: (payload: QuestionFormState) => Promise<void>;
  onCloneRequired: () => void;
};

export function QuestionForm({ mode, initialValue, onSave, onCloneRequired }: QuestionFormProps) {
  const [form, setForm] = useState<QuestionFormState>(initialValue);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<"ui" | "signal">("ui");

  const dirty = useDirtyFormState(initialValue, form);
  useUnsavedChangesGuard(dirty);

  const requiresOptions = useMemo(
    () => ["forced_choice", "situational", "single_select", "multi_select", "multi_select_or_ranking"].includes(form.question_type),
    [form.question_type]
  );

  const hasPrimaryWeight = typeof form.weights_by_dimension_json[form.primary_dimension] === "number";
  const hasInvalidQuestionWeight = Object.values(form.weights_by_dimension_json).some((value) => typeof value !== "number");
  const hasInvalidOptionWeight = form.options_json.some((option) => {
    const optionWeights = option.weights_by_dimension;
    if (!optionWeights) return false;
    return Object.values(optionWeights).some((value) => typeof value !== "number");
  });
  const boundaryMetadataIsValid = form.boundary_metadata_json === null || typeof form.boundary_metadata_json === "object";

  const invalid =
    !form.assessment_version_slug.trim() ||
    !form.question_id.trim() ||
    !form.block.trim() ||
    !form.text.trim() ||
    !form.primary_dimension.trim() ||
    !form.question_purpose.trim() ||
    !hasPrimaryWeight ||
    hasInvalidQuestionWeight ||
    hasInvalidOptionWeight ||
    !boundaryMetadataIsValid ||
    (requiresOptions && form.options_json.length === 0);

  const handleTypeChange = (nextType: string) => {
    setForm((prev) => {
      if (nextType === "likert" && prev.options_json.length === 0) {
        return { ...prev, question_type: nextType, options_json: DEFAULT_LIKERT_OPTIONS };
      }
      return { ...prev, question_type: nextType };
    });
  };

  const handleSave = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setSuccess(null);
    setError(null);
    try {
      await onSave(form);
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

  const toggleSecondary = (dimension: string) => {
    setForm((prev) => {
      const exists = prev.secondary_dimensions.includes(dimension);
      return {
        ...prev,
        secondary_dimensions: exists
          ? prev.secondary_dimensions.filter((item) => item !== dimension)
          : [...prev.secondary_dimensions, dimension],
      };
    });
  };

  return (
    <form className="admin-form" onSubmit={handleSave}>
      <div className="admin-form-header">
        <h2>{mode === "create" ? "Новый вопрос" : `${form.assessment_version_slug} / ${form.question_id}`}</h2>
        <DirtyIndicator dirty={dirty} />
      </div>

      <div className="admin-grid-two">
        <label className="admin-field">
          <span>Assessment Slug</span>
          <input className="admin-input" value={form.assessment_version_slug} onChange={(e) => setForm((prev) => ({ ...prev, assessment_version_slug: e.target.value }))} disabled={mode === "edit"} />
        </label>
        <label className="admin-field">
          <span>Question ID</span>
          <input className="admin-input" value={form.question_id} onChange={(e) => setForm((prev) => ({ ...prev, question_id: e.target.value }))} disabled={mode === "edit"} />
        </label>
      </div>

      <div className="admin-grid-two">
        <label className="admin-field">
          <span>Block</span>
          <input className="admin-input" value={form.block} onChange={(e) => setForm((prev) => ({ ...prev, block: e.target.value }))} />
        </label>
        <label className="admin-field">
          <span>Subblock</span>
          <input className="admin-input" value={form.subblock} onChange={(e) => setForm((prev) => ({ ...prev, subblock: e.target.value }))} />
        </label>
      </div>

      <label className="admin-field">
        <span>Question Type</span>
        <select className="admin-input" value={form.question_type} onChange={(e) => handleTypeChange(e.target.value)}>
          {QUESTION_TYPES.map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </label>

      <label className="admin-field">
        <span>Text</span>
        <textarea className="admin-textarea" value={form.text} onChange={(e) => setForm((prev) => ({ ...prev, text: e.target.value }))} rows={3} />
      </label>

      <div className="admin-grid-two">
        <label className="admin-field">
          <span>Primary Dimension</span>
          <select className="admin-input" value={form.primary_dimension} onChange={(e) => setForm((prev) => ({ ...prev, primary_dimension: e.target.value }))}>
            {DIMENSIONS.map((dim) => <option key={dim} value={dim}>{dim}</option>)}
          </select>
        </label>
        <label className="admin-field">
          <span>Status</span>
          <select className="admin-input" value={form.status} onChange={(e) => setForm((prev) => ({ ...prev, status: e.target.value }))}>
            <option value="draft">draft</option>
            <option value="active">active</option>
            <option value="archive">archive</option>
          </select>
        </label>
      </div>

      <div className="admin-editor-box">
        <div className="admin-editor-box-title">Secondary Dimensions</div>
        <div className="admin-chip-grid">
          {DIMENSIONS.map((dim) => {
            const selected = form.secondary_dimensions.includes(dim);
            return (
              <button
                key={dim}
                type="button"
                className={`admin-chip ${selected ? "admin-chip-active" : ""}`}
                onClick={() => toggleSecondary(dim)}
              >
                {dim}
              </button>
            );
          })}
        </div>
      </div>

      <DimensionWeightsEditor value={form.weights_by_dimension_json} onChange={(next) => setForm((prev) => ({ ...prev, weights_by_dimension_json: next }))} />

      <OptionsEditor value={form.options_json} onChange={(next) => setForm((prev) => ({ ...prev, options_json: next }))} readOnly={form.question_type === "multi_select_or_ranking"} />
      {form.question_type === "multi_select_or_ranking" && (
        <div className="admin-help">Тип multi_select_or_ranking в Phase 1 поддерживается в guarded режиме: доступно чтение и сохранение без расширенной интерактивной логики.</div>
      )}

      <div className="admin-grid-two">
        <label className="admin-field">
          <span>Purpose</span>
          <input className="admin-input" value={form.question_purpose} onChange={(e) => setForm((prev) => ({ ...prev, question_purpose: e.target.value }))} />
        </label>
        <label className="admin-field">
          <span>Order Hint</span>
          <input type="number" className="admin-input" value={form.order_hint} onChange={(e) => setForm((prev) => ({ ...prev, order_hint: Number(e.target.value) }))} />
        </label>
      </div>

      <div className="admin-grid-two">
        <label className="admin-field">
          <span>Experiment mode</span>
          <input className="admin-input" value={form.experiment_mode} onChange={(e) => setForm((prev) => ({ ...prev, experiment_mode: e.target.value }))} placeholder="baseline / baseline+expansion_p0_v1" />
        </label>
        <label className="admin-field">
          <span>Experiment tag</span>
          <input className="admin-input" value={form.experiment_tag} onChange={(e) => setForm((prev) => ({ ...prev, experiment_tag: e.target.value }))} placeholder="expansion_p0_v1" />
        </label>
      </div>

      <div className="admin-grid-two">
        <label className="admin-field">
          <span>Active in scoring</span>
          <select className="admin-input" value={form.active_in_scoring ? "yes" : "no"} onChange={(e) => setForm((prev) => ({ ...prev, active_in_scoring: e.target.value === "yes" }))}>
            <option value="yes">yes</option>
            <option value="no">no</option>
          </select>
        </label>
        <label className="admin-field">
          <span>Boundary metadata (optional JSON)</span>
          <textarea
            className="admin-textarea"
            value={form.boundary_metadata_json ? JSON.stringify(form.boundary_metadata_json) : ""}
            onChange={(e) => {
              const next = e.target.value.trim();
              if (!next) {
                setError(null);
                setForm((prev) => ({ ...prev, boundary_metadata_json: null }));
                return;
              }
              try {
                const parsed = JSON.parse(next) as Record<string, unknown>;
                setError(null);
                setForm((prev) => ({ ...prev, boundary_metadata_json: parsed }));
              } catch {
                setError("Boundary metadata должен быть корректным JSON-объектом");
              }
            }}
            rows={2}
          />
        </label>
      </div>

      <label className="admin-field">
        <span>Notes</span>
        <textarea className="admin-textarea" value={form.notes} onChange={(e) => setForm((prev) => ({ ...prev, notes: e.target.value }))} rows={2} />
      </label>

      <div className="admin-preview-tabs">
        <button type="button" className={`admin-tab ${tab === "ui" ? "admin-tab-active" : ""}`} onClick={() => setTab("ui")}>UI Preview</button>
        <button type="button" className={`admin-tab ${tab === "signal" ? "admin-tab-active" : ""}`} onClick={() => setTab("signal")}>Signal Preview</button>
      </div>

      {tab === "ui" ? (
        <QuestionPreviewCard questionType={form.question_type} text={form.text} options={form.options_json} />
      ) : (
        <SignalPreviewPanel questionType={form.question_type} optionsJson={form.options_json} weightsByDimension={form.weights_by_dimension_json} />
      )}

      <div className="admin-form-actions">
        <button className="admin-btn admin-btn-primary" type="submit" disabled={saving || invalid || !dirty}>
          {saving ? "Сохранение..." : "Сохранить"}
        </button>
      </div>

      <FormFeedback success={success} error={error} />
    </form>
  );
}
