"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { AssessmentForm } from "@/components/admin/assessment-form";
import { CloneVersionModal } from "@/components/admin/clone-version-modal";
import { adminFetch } from "@/lib/admin-api";

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

export default function AssessmentEditorPage() {
  const params = useParams<{ slug: string }>();
  const router = useRouter();
  const [value, setValue] = useState<Assessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [cloneOpen, setCloneOpen] = useState(false);
  const [cloneLoading, setCloneLoading] = useState(false);

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      try {
        const data = await adminFetch<Assessment>(`/admin/assessments/${params.slug}`);
        setValue(data);
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [params.slug]);

  if (loading || !value) {
    return <div className="admin-loading">Загрузка...</div>;
  }

  return (
    <section className="admin-page">
      <h1>Assessment Editor</h1>
      <AssessmentForm
        value={value}
        loading={loading}
        onSave={async (patch) => {
          const updated = await adminFetch<Assessment>(`/admin/assessments/${params.slug}`, {
            method: "PATCH",
            body: JSON.stringify(patch),
          });
          setValue(updated);
        }}
        onCloneRequired={() => setCloneOpen(true)}
      />

      <CloneVersionModal
        open={cloneOpen}
        title="Нужен draft-клон"
        description="Активную версию нельзя редактировать напрямую. Создать draft-клон и перейти к нему."
        loading={cloneLoading}
        onCancel={() => setCloneOpen(false)}
        onConfirm={async () => {
          setCloneLoading(true);
          try {
            const result = await adminFetch<{ draft_slug: string }>(`/admin/assessments/${params.slug}/clone`, {
              method: "POST",
              body: JSON.stringify({}),
            });
            router.replace(`/admin/assessments/${result.draft_slug}`);
          } finally {
            setCloneLoading(false);
            setCloneOpen(false);
          }
        }}
      />
    </section>
  );
}
