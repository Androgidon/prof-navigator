"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { CloneVersionModal } from "@/components/admin/clone-version-modal";
import { QuestionForm, type QuestionFormState } from "@/components/admin/question-form";
import { adminFetch } from "@/lib/admin-api";

type QuestionResponse = {
  assessment_version_slug: string;
  question_id: string;
  block: string;
  subblock?: string | null;
  question_type: string;
  text: string;
  primary_dimension: string;
  secondary_dimensions?: string[];
  weights_by_dimension_json?: Record<string, number>;
  options_json?: Array<{ key: string; label: string; weights_by_dimension?: Record<string, number> }>;
  consistency_pair_id?: string | null;
  difficulty?: string | null;
  is_required: boolean;
  order_hint: number;
  status: string;
  question_purpose: string;
  notes?: string | null;
};

function mapToForm(value: QuestionResponse): QuestionFormState {
  return {
    assessment_version_slug: value.assessment_version_slug,
    question_id: value.question_id,
    block: value.block,
    subblock: value.subblock ?? "",
    question_type: value.question_type,
    text: value.text,
    primary_dimension: value.primary_dimension,
    secondary_dimensions: value.secondary_dimensions ?? [],
    weights_by_dimension_json: value.weights_by_dimension_json ?? {},
    options_json: value.options_json ?? [],
    consistency_pair_id: value.consistency_pair_id ?? "",
    difficulty: value.difficulty ?? "",
    is_required: value.is_required,
    order_hint: value.order_hint,
    status: value.status,
    question_purpose: value.question_purpose,
    notes: value.notes ?? "",
  };
}

export default function QuestionEditorPage() {
  const params = useParams<{ assessmentSlug: string; questionId: string }>();
  const router = useRouter();
  const [value, setValue] = useState<QuestionFormState | null>(null);
  const [loading, setLoading] = useState(true);
  const [cloneOpen, setCloneOpen] = useState(false);
  const [cloneLoading, setCloneLoading] = useState(false);

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      try {
        const data = await adminFetch<QuestionResponse>(`/admin/questions/${params.assessmentSlug}/${params.questionId}`);
        setValue(mapToForm(data));
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [params.assessmentSlug, params.questionId]);

  const initial = useMemo(() => value, [value]);

  if (loading || !initial) {
    return <div className="admin-loading">Загрузка...</div>;
  }

  return (
    <section className="admin-page">
      <h1>Question Editor</h1>
      <QuestionForm
        mode="edit"
        initialValue={initial}
        onSave={async (payload) => {
          const patch = {
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
            order_hint: payload.order_hint,
            status: payload.status,
            question_purpose: payload.question_purpose,
            notes: payload.notes || null,
          };
          const updated = await adminFetch<QuestionResponse>(`/admin/questions/${params.assessmentSlug}/${params.questionId}`, {
            method: "PATCH",
            body: JSON.stringify(patch),
          });
          setValue(mapToForm(updated));
        }}
        onCloneRequired={() => setCloneOpen(true)}
      />

      <CloneVersionModal
        open={cloneOpen}
        title="Редактирование active вопроса"
        description="Сначала создайте draft assessment clone, затем склонируйте этот вопрос в draft-версию."
        loading={cloneLoading}
        onCancel={() => setCloneOpen(false)}
        onConfirm={async () => {
          setCloneLoading(true);
          try {
            const draft = await adminFetch<{ draft_slug: string }>(`/admin/assessments/${params.assessmentSlug}/clone`, {
              method: "POST",
              body: JSON.stringify({}),
            });
            const cloned = await adminFetch<{ assessment_version_slug: string; question_id: string }>(
              `/admin/questions/${params.assessmentSlug}/${params.questionId}/clone`,
              {
                method: "POST",
                body: JSON.stringify({ target_assessment_version_slug: draft.draft_slug }),
              }
            );
            router.replace(`/admin/questions/${cloned.assessment_version_slug}/${cloned.question_id}`);
          } finally {
            setCloneLoading(false);
            setCloneOpen(false);
          }
        }}
      />
    </section>
  );
}
