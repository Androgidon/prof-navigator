"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ProfessionForm, type ProfessionFormState } from "@/components/admin/profession-form";
import { adminFetch } from "@/lib/admin-api";

type ProfessionResponse = {
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

function mapForm(value: ProfessionResponse): ProfessionFormState {
  return {
    external_id: value.external_id,
    slug: value.slug,
    title: value.title,
    cluster: value.cluster,
    summary: value.summary,
    status: value.status,
    matrix_version_slug: value.matrix_version_slug,
    first_steps_short: value.first_steps_short || [],
    important_subjects_short: value.important_subjects_short || [],
  };
}

export default function EditProfessionPage() {
  const params = useParams<{ slug: string }>();
  const [value, setValue] = useState<ProfessionFormState | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      try {
        const data = await adminFetch<ProfessionResponse>(`/admin/professions/${params.slug}`);
        setValue(mapForm(data));
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
      <h1>Редактор профессии</h1>
      <ProfessionForm
        mode="edit"
        initialValue={value}
        onSave={async (payload) => {
          const updated = await adminFetch<ProfessionResponse>(`/admin/professions/${params.slug}`, {
            method: "PATCH",
            body: JSON.stringify({
              title: payload.title,
              cluster: payload.cluster,
              summary: payload.summary,
              status: payload.status,
              first_steps_short: payload.first_steps_short,
              important_subjects_short: payload.important_subjects_short,
              matrix_version_slug: payload.matrix_version_slug,
            }),
          });
          setValue(mapForm(updated));
        }}
      />
    </section>
  );
}
