"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { MatrixForm, type MatrixFormState } from "@/components/admin/matrix-form";
import { adminFetch } from "@/lib/admin-api";

type MatrixResponse = {
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
  notes?: string | null;
};

function mapForm(value: MatrixResponse): MatrixFormState {
  return {
    profession_slug: value.profession_slug,
    profession_title: value.profession_title,
    cluster: value.cluster,
    version_slug: value.version_slug,
    matrix_version: value.matrix_version,
    target_profile_json: value.target_profile_json || {},
    dimension_weights_json: value.dimension_weights_json || {},
    critical_dimensions: value.critical_dimensions || [],
    important_subjects: value.important_subjects || [],
    hobby_signals: value.hobby_signals || [],
    preferred_environments: value.preferred_environments || [],
    why_fit_template: value.why_fit_template || "",
    first_steps_template: value.first_steps_template || [],
    notes: value.notes || "",
  };
}

export default function MatrixEditorPage() {
  const params = useParams<{ versionSlug: string; professionSlug: string }>();
  const router = useRouter();
  const [value, setValue] = useState<MatrixFormState | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      try {
        const data = await adminFetch<MatrixResponse>(`/admin/matrix/${params.versionSlug}/${params.professionSlug}`);
        setValue(mapForm(data));
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [params.professionSlug, params.versionSlug]);

  if (loading || !value) {
    return <div className="admin-loading">Загрузка...</div>;
  }

  return (
    <section className="admin-page">
      <h1>Matrix Editor</h1>
      <MatrixForm
        initialValue={value}
        onSaved={(next) => setValue(next)}
        onCloned={(versionSlug, professionSlug) => {
          router.replace(`/admin/matrix/${versionSlug}/${professionSlug}`);
        }}
      />
    </section>
  );
}
