"use client";

import { useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { CloneVersionModal } from "@/components/admin/clone-version-modal";
import { QuestionForm, type QuestionFormState } from "@/components/admin/question-form";
import { DEFAULT_LIKERT_OPTIONS } from "@/lib/question-defaults";
import { adminFetch } from "@/lib/admin-api";

function createInitial(assessmentSlug: string): QuestionFormState {
  return {
    assessment_version_slug: assessmentSlug,
    question_id: "",
    block: "interests_and_task_preferences",
    subblock: "",
    question_type: "likert",
    text: "",
    primary_dimension: "analytical",
    secondary_dimensions: [],
    weights_by_dimension_json: { analytical: 1 },
    options_json: DEFAULT_LIKERT_OPTIONS,
    consistency_pair_id: "",
    difficulty: "",
    is_required: true,
    active_in_scoring: true,
    experiment_tag: "",
    experiment_mode: "",
    boundary_metadata_json: null,
    order_hint: 0,
    status: "draft",
    question_purpose: "",
    notes: "",
  };
}

export default function NewQuestionPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const assessmentSlug = searchParams.get("assessmentSlug") ?? "";
  const [cloneOpen, setCloneOpen] = useState(false);

  const initial = useMemo(() => createInitial(assessmentSlug), [assessmentSlug]);

  return (
    <section className="admin-page">
      <h1>Новый вопрос</h1>
      <QuestionForm
        mode="create"
        initialValue={initial}
        onSave={async (payload) => {
          const body = {
            assessment_version_slug: payload.assessment_version_slug,
            question_id: payload.question_id,
            block: payload.block,
            subblock: payload.subblock || null,
            question_type: payload.question_type,
            text: payload.text,
            options_json: payload.options_json,
            primary_dimension: payload.primary_dimension,
            secondary_dimensions: payload.secondary_dimensions,
            weights_by_dimension_json: payload.weights_by_dimension_json,
            consistency_pair_id: payload.consistency_pair_id || null,
            difficulty: payload.difficulty || null,
            is_required: payload.is_required,
            active_in_scoring: payload.active_in_scoring,
            experiment_tag: payload.experiment_tag || null,
            experiment_mode: payload.experiment_mode || null,
            boundary_metadata_json: payload.boundary_metadata_json,
            status: payload.status,
            question_purpose: payload.question_purpose,
            notes: payload.notes || null,
            order_hint: payload.order_hint > 0 ? payload.order_hint : undefined,
          };
          const created = await adminFetch<{ assessment_version_slug: string; question_id: string }>("/admin/questions", {
            method: "POST",
            body: JSON.stringify(body),
          });
          router.replace(`/admin/questions/${created.assessment_version_slug}/${created.question_id}`);
        }}
        onCloneRequired={() => setCloneOpen(true)}
      />

      <CloneVersionModal
        open={cloneOpen}
        title="Нельзя создавать в active версии"
        description="Создайте draft assessment и укажите его assessmentSlug в форме создания вопроса."
        onCancel={() => setCloneOpen(false)}
        onConfirm={() => setCloneOpen(false)}
      />
    </section>
  );
}
