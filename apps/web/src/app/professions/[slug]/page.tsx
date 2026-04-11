"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { ProfessionHero } from "@/components/layout/profession-hero";
import { ContentPanel, SubjectsList } from "@/components/layout/content-panel";
import { ActionList } from "@/components/layout/action-list";
import { RelatedProfessions } from "@/components/layout/related-professions";

type RelatedProfession = {
  slug: string;
  title: string;
  cluster: string;
};

type ProfessionDetail = {
  slug: string;
  title: string;
  cluster: string;
  summary: string;
  status: string;
  what_specialist_does: string;
  who_suits: string[];
  important_subjects: string[];
  required_skills: string[];
  how_to_start: string[];
  related_professions: RelatedProfession[];
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

function normalizeText(value: string | undefined, fallback: string): string {
  const text = (value ?? "").trim();
  return text.length > 0 ? text : fallback;
}

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
          if (response.status === 404) {
            throw new Error("Профессия не найдена или пока недоступна");
          }
          throw new Error("Не удалось загрузить данные о профессии");
        }
        const data = (await response.json()) as ProfessionDetail;
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
          <div className="error-state">{error || "Профессия не найдена"}</div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  const whoSuits = profession.who_suits.length > 0
    ? profession.who_suits
    : ["Подходит тем, кто хочет развиваться в этой сфере и пробовать практические задачи."];

  const importantSubjects = profession.important_subjects.length > 0
    ? profession.important_subjects
    : ["Список предметов пока дополняется."];

  const requiredSkills = profession.required_skills.length > 0
    ? profession.required_skills
    : ["Базовые навыки коммуникации", "Самоорганизация", "Готовность учиться на практике"];

  const howToStart = profession.how_to_start.length > 0
    ? profession.how_to_start
    : ["Изучить базовые материалы по направлению", "Сделать первый учебный проект", "Проконсультироваться с наставником или специалистом"];

  return (
    <div className="profession-detail-page">
      <SiteHeader />

      <main className="profession-detail-content">
        <ProfessionHero
          title={profession.title}
          category={profession.cluster}
          isFavorited={isFavorited}
          onFavorite={() => setIsFavorited(!isFavorited)}
          backHref="/professions"
          backLabel="Назад к каталогу"
        />

        <ContentPanel title="Краткое описание">
          <p>{normalizeText(profession.summary, "Краткое описание пока дополняется.")}</p>
        </ContentPanel>

        <ContentPanel title="Чем занимается специалист">
          <p>{normalizeText(profession.what_specialist_does, "Описание задач специалиста пока дополняется.")}</p>
        </ContentPanel>

        <ContentPanel title="Кому подходит">
          <ul className="list-disc pl-5 space-y-1">
            {whoSuits.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        </ContentPanel>

        <ContentPanel title="Важные предметы">
          <SubjectsList subjects={importantSubjects} />
        </ContentPanel>

        <ContentPanel title="Нужные навыки">
          <ul className="list-disc pl-5 space-y-1">
            {requiredSkills.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        </ContentPanel>

        <ActionList
          title="Как начать"
          items={howToStart.map((step) => ({ title: step }))}
        />

        {profession.related_professions.length > 0 && (
          <RelatedProfessions
            title="Похожие профессии"
            items={profession.related_professions.map((item) => ({
              title: item.title,
              slug: item.slug,
            }))}
          />
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
