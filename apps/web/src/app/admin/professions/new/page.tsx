"use client";

import { useRouter } from "next/navigation";
import { ProfessionForm, type ProfessionFormState } from "@/components/admin/profession-form";
import { adminFetch } from "@/lib/admin-api";

const initial: ProfessionFormState = {
  external_id: 0,
  slug: "",
  title: "",
  cluster: "",
  summary: "",
  status: "draft",
  matrix_version_slug: "matrix_v1",
  first_steps_short: [],
  important_subjects_short: [],
};

export default function NewProfessionPage() {
  const router = useRouter();

  return (
    <section className="admin-page">
      <h1>Новая профессия</h1>
      <ProfessionForm
        mode="create"
        initialValue={initial}
        onSave={async (payload) => {
          const created = await adminFetch<{ slug: string }>("/admin/professions", {
            method: "POST",
            body: JSON.stringify(payload),
          });
          router.replace(`/admin/professions/${created.slug}`);
        }}
      />
    </section>
  );
}
