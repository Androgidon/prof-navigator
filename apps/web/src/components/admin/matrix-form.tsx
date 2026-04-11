"use client";

import { useState } from "react";
import { CloneVersionModal } from "@/components/admin/clone-version-modal";
import { DirtyIndicator } from "@/components/admin/dirty-indicator";
import { FormFeedback } from "@/components/admin/form-feedback";
import { MatrixDimensionEditor } from "@/components/admin/matrix-dimension-editor";
import { MatrixPreviewPanel } from "@/components/admin/matrix-preview-panel";
import { MatrixSignalsEditor } from "@/components/admin/matrix-signals-editor";
import { MatrixValidationPanel } from "@/components/admin/matrix-validation-panel";
import { SliderDimensionGrid } from "@/components/admin/slider-dimension-grid";
import { useDirtyFormState } from "@/hooks/use-dirty-form-state";
import { useUnsavedChangesGuard } from "@/hooks/use-unsaved-changes-guard";
import { adminFetch } from "@/lib/admin-api";
import { DIMENSIONS } from "@/lib/question-defaults";

export type MatrixFormState = {
  profession_slug: string;
  profession_title: string;
  cluster: string;
  version_slug: string;
  matrix_version: number;
  target_profile_json: Record<string, number>;
  dimension_weights_json: Record<string, number>;
  critical_dimensions: string[];
  important_subjects: string[];
  hobby_signals: string[];
  preferred_environments: string[];
  why_fit_template: string;
  first_steps_template: string[];
  notes: string;
};

type ValidationIssue = {
  severity: string;
  code: string;
  message: string;
};

type MatrixFormProps = {
  initialValue: MatrixFormState;
  onSaved: (next: MatrixFormState) => void;
  onCloned: (versionSlug: string, professionSlug: string) => void;
};

type MatrixPreviewResult = {
  base_similarity: number;
  critical_penalty: number;
  strong_fit_effect: number;
  admissibility_effect: number;
  admissible: boolean;
  final_score: number;
};

const defaultProfile = Object.fromEntries(DIMENSIONS.map((dim) => [dim, 50]));

const presets: Record<string, Record<string, number>> = {
  balanced: defaultProfile,
  tech: {
    ...defaultProfile,
    technical: 85,
    analytical: 80,
    detail: 78,
    practical: 70,
    social: 40,
  },
  creative: {
    ...defaultProfile,
    creative: 90,
    exploratory: 82,
    verbal: 76,
    structured: 38,
  },
  social: {
    ...defaultProfile,
    social: 88,
    helping: 84,
    verbal: 80,
    leadership: 72,
    quantitative: 42,
  },
};

export function MatrixForm({ initialValue, onSaved, onCloned }: MatrixFormProps) {
  const [form, setForm] = useState(initialValue);
  const [sampleProfile, setSampleProfile] = useState<Record<string, number>>(presets.balanced);
  const [previewResult, setPreviewResult] = useState<MatrixPreviewResult | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [validation, setValidation] = useState<{ valid: boolean; completeness_score: number; hard_errors: ValidationIssue[]; warnings: ValidationIssue[] }>({
    valid: true,
    completeness_score: 0,
    hard_errors: [],
    warnings: [],
  });
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cloneOpen, setCloneOpen] = useState(false);
  const [cloneLoading, setCloneLoading] = useState(false);

  const dirty = useDirtyFormState(initialValue, form);
  useUnsavedChangesGuard(dirty);

  const runValidation = async () => {
    const result = await adminFetch<{ valid: boolean; completeness_score: number; hard_errors: ValidationIssue[]; warnings: ValidationIssue[] }>(
      "/admin/matrix/validate",
      {
        method: "POST",
        body: JSON.stringify({
          target_profile_json: form.target_profile_json,
          dimension_weights_json: form.dimension_weights_json,
          critical_dimensions: form.critical_dimensions,
          why_fit_template: form.why_fit_template,
        }),
      }
    );
    setValidation(result);
    return result;
  };

  const invalid = !dirty || saving || validation.hard_errors.length > 0;

  return (
    <form
      className="admin-form"
      onSubmit={async (event) => {
        event.preventDefault();
        setSaving(true);
        setSuccess(null);
        setError(null);
        try {
          const v = await runValidation();
          if (!v.valid) {
            setError("Validation содержит hard errors");
            return;
          }
          const updated = await adminFetch<MatrixFormState>(`/admin/matrix/${form.version_slug}/${form.profession_slug}`, {
            method: "PATCH",
            body: JSON.stringify({
              target_profile_json: form.target_profile_json,
              dimension_weights_json: form.dimension_weights_json,
              critical_dimensions: form.critical_dimensions,
              important_subjects: form.important_subjects,
              hobby_signals: form.hobby_signals,
              preferred_environments: form.preferred_environments,
              why_fit_template: form.why_fit_template,
              first_steps_template: form.first_steps_template,
              notes: form.notes || null,
            }),
          });
          setForm(updated);
          onSaved(updated);
          setSuccess("Сохранено");
        } catch (err) {
          const e = err as Error & { code?: string };
          if (e.code === "requires_clone") {
            setCloneOpen(true);
            return;
          }
          setError(e.message || "Ошибка сохранения");
        } finally {
          setSaving(false);
        }
      }}
    >
      <div className="admin-form-header">
        <h2>{form.profession_slug} / {form.version_slug}</h2>
        <DirtyIndicator dirty={dirty} />
      </div>

      <MatrixDimensionEditor
        targets={form.target_profile_json}
        weights={form.dimension_weights_json}
        onTargetsChange={(next) => setForm((prev) => ({ ...prev, target_profile_json: next }))}
        onWeightsChange={(next) => setForm((prev) => ({ ...prev, dimension_weights_json: next }))}
      />

      <MatrixSignalsEditor
        critical_dimensions={form.critical_dimensions}
        important_subjects={form.important_subjects}
        hobby_signals={form.hobby_signals}
        preferred_environments={form.preferred_environments}
        first_steps_template={form.first_steps_template}
        onChange={(patch) => setForm((prev) => ({ ...prev, ...patch }))}
      />

      <label className="admin-field">
        <span>Why Fit Template</span>
        <textarea className="admin-textarea" rows={3} value={form.why_fit_template} onChange={(e) => setForm((prev) => ({ ...prev, why_fit_template: e.target.value }))} />
      </label>

      <label className="admin-field">
        <span>Notes</span>
        <textarea className="admin-textarea" rows={2} value={form.notes} onChange={(e) => setForm((prev) => ({ ...prev, notes: e.target.value }))} />
      </label>

      <SliderDimensionGrid value={sampleProfile} onChange={setSampleProfile} />
      <div className="admin-form-actions">
        <button type="button" className="admin-btn admin-btn-ghost" onClick={() => setSampleProfile(presets.tech)}>Preset: Tech</button>
        <button type="button" className="admin-btn admin-btn-ghost" onClick={() => setSampleProfile(presets.creative)}>Preset: Creative</button>
        <button type="button" className="admin-btn admin-btn-ghost" onClick={() => setSampleProfile(presets.social)}>Preset: Social</button>
        <button type="button" className="admin-btn admin-btn-ghost" onClick={() => setSampleProfile(presets.balanced)}>Preset: Balanced</button>
        <button type="button" className="admin-btn admin-btn-ghost" onClick={() => { setSampleProfile(defaultProfile); setPreviewResult(null); setPreviewError(null); }}>Reset Preview</button>
      </div>

      <MatrixPreviewPanel
        cluster={form.cluster}
        profileScores={sampleProfile}
        targetProfile={form.target_profile_json}
        weights={form.dimension_weights_json}
        criticalDimensions={form.critical_dimensions}
        onResult={(result, err) => {
          setPreviewResult(result);
          setPreviewError(err);
        }}
      />

      {previewError && <div className="admin-error">{previewError}</div>}
      {previewResult && (
        <div className="admin-editor-box">
          <p>base similarity: {previewResult.base_similarity}</p>
          <p>critical penalty: {previewResult.critical_penalty}</p>
          <p>strong-fit effect: {previewResult.strong_fit_effect}</p>
          <p>admissibility effect: {previewResult.admissibility_effect}</p>
          <p>final score: {previewResult.final_score}</p>
        </div>
      )}

      <div className="admin-form-actions">
        <button type="button" className="admin-btn admin-btn-ghost" onClick={() => void runValidation()}>
          Validate
        </button>
        <button type="submit" className="admin-btn admin-btn-primary" disabled={invalid}>
          {saving ? "Сохранение..." : "Сохранить"}
        </button>
      </div>

      <MatrixValidationPanel
        valid={validation.valid}
        completenessScore={validation.completeness_score}
        hardErrors={validation.hard_errors}
        warnings={validation.warnings}
      />

      <FormFeedback success={success} error={error} />

      <CloneVersionModal
        open={cloneOpen}
        title="Нужен draft matrix clone"
        description="Активную matrix-версию нельзя редактировать напрямую."
        loading={cloneLoading}
        onCancel={() => setCloneOpen(false)}
        onConfirm={async () => {
          setCloneLoading(true);
          try {
            const clone = await adminFetch<{ draft_version_slug: string; profession_slug: string }>(
              `/admin/matrix/${form.version_slug}/${form.profession_slug}/clone`,
              { method: "POST", body: JSON.stringify({}) }
            );
            onCloned(clone.draft_version_slug, clone.profession_slug);
          } finally {
            setCloneLoading(false);
            setCloneOpen(false);
          }
        }}
      />
    </form>
  );
}
