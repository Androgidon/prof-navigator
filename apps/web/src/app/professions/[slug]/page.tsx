"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { ProfessionHero } from "@/components/layout/profession-hero";
import { FactsRow } from "@/components/layout/facts-row";
import { ContentPanel, SubjectsList } from "@/components/layout/content-panel";
import { ActionList } from "@/components/layout/action-list";

type ProfessionDetail = {
  slug: string;
  title_ru: string;
  description: string | null;
  important_subjects: string[];
  start_now_steps: string[];
  industry?: string;
  salary_range?: string;
  demand_level?: string;
  education_level?: string;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export default function ProfessionDetailPage() {
  const params = useParams();
  const slug = params?.slug as string;

  const [profession, setProfession] = useState<ProfessionDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isFavorited, setIsFavorited] = useState(false);

  useEffect(() => {
    if (!slug) return;

    const controller = new AbortController();

    const fetchProfession = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${apiUrl}/professions/${slug}`, {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error("Профессия не найдена");
        }
        const data = await response.json();
        setProfession(data);
      } catch (err) {
        if ((err as Error).name !== "AbortError") {
          setError(err instanceof Error ? err.message : "Ошибка при загрузке");
        }
      } finally {
        setLoading(false);
      }
    };

    void fetchProfession();
    return () => controller.abort();
  }, [slug]);

  if (loading) {
    return (
      <div className="profession-detail-page">
        <SiteHeader />
        <main className="profession-detail-content">
          <div className="loading-state">Загружаем информацию о профессии...</div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  if (error || !profession) {
    return (
      <div className="profession-detail-page">
        <SiteHeader />
        <main className="profession-detail-content">
          <div className="error-state">
            {error || "Профессия не найдена"}
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  const hasSubjects = profession.important_subjects?.length > 0;
  const hasSteps = profession.start_now_steps?.length > 0;

  return (
    <div className="profession-detail-page">
      <SiteHeader />

      <main className="profession-detail-content">
        <ProfessionHero
          title={profession.title_ru}
          category={profession.industry || "Профессия"}
          isFavorited={isFavorited}
          onFavorite={() => setIsFavorited(!isFavorited)}
        />

        <FactsRow
          salary={profession.salary_range}
          demand={profession.demand_level}
          education={profession.education_level}
        />

        {profession.description && (
          <ContentPanel title="Описание профессии">
            <p>{profession.description}</p>
          </ContentPanel>
        )}

        {hasSubjects && (
          <ContentPanel title="Важные предметы">
            <SubjectsList subjects={profession.important_subjects} />
          </ContentPanel>
        )}

        {hasSteps && (
          <ActionList
            items={profession.start_now_steps.map((step, i) => ({
              title: step,
              description: `Шаг ${i + 1}`,
            }))}
          />
        )}
      </main>

      <SiteFooter />
    </div>
  );
}