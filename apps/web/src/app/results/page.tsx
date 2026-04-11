"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { ProfileSummaryHero } from "@/components/layout/profile-summary-hero";
import { RecommendationCard } from "@/components/layout/recommendation-card";
import { ExplanationPanel, ExplanationItem } from "@/components/layout/explanation-panel";
import { authFetch, AuthExpiredError } from "@/lib/api-client";

type AssessmentRecommendation = {
  slug: string;
  profession?: string;
  title?: string;
  score?: number;
  match_score?: number;
  summary?: string;
  why_fit?: string;
  cluster?: string;
  explanation?: string[];
};

type TopStrengthItem = {
  title?: string;
  description?: string;
  summary?: string;
  dimension?: string;
  score?: number;
};

type AssessmentResultPayload = {
  result_id: string;
  session_id: string;
  assessment_slug: string;
  status: string;
  profile_scores: Record<string, number>;
  profile_summary: Record<string, unknown>;
  top_strengths?: TopStrengthItem[];
  recommendations: AssessmentRecommendation[];
  confidence: Record<string, unknown>;
};

type FavoritesState = Record<string, boolean>;

function deriveArchetype(profileScores: Record<string, number>): string {
  const sorted = Object.entries(profileScores).sort((a, b) => b[1] - a[1]);
  const top = sorted.slice(0, 2).map(([k]) => k);
  if (top.includes("technical") && top.includes("analytical")) return "Техно-аналитик";
  if (top.includes("social") && top.includes("helping")) return "Коммуникатор-наставник";
  if (top.includes("creative") && top.includes("exploratory")) return "Креативный исследователь";
  if (top.includes("structured") && top.includes("detail")) return "Системный организатор";
  return "Профиль учащегося";
}

function strengthDescription(item: TopStrengthItem): string {
  if (item.description && item.description.trim().length > 0) return item.description;
  if (item.summary && item.summary.trim().length > 0) return item.summary;
  if (item.dimension && item.dimension.trim().length > 0) {
    return `Высокий показатель по направлению ${item.dimension}.`;
  }
  return "Сильная сторона по результатам вашего прохождения теста.";
}

export default function ResultsPage() {
  const searchParams = useSearchParams();
  const resultId = searchParams.get("result_id");

  const [result, setResult] = useState<AssessmentResultPayload | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [favorites, setFavorites] = useState<FavoritesState>({});

  useEffect(() => {
    if (!resultId) {
      setError("Не найден result_id. Пройдите тест заново.");
      return;
    }

    const controller = new AbortController();

    const fetchResult = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await authFetch(`/assessments/results/${resultId}`, {
          method: "GET",
          signal: controller.signal,
        });
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error("Результат не найден или недоступен");
          }
          throw new Error("Не удалось получить результаты теста");
        }
        const payload = (await response.json()) as AssessmentResultPayload;
        setResult(payload);
      } catch (err) {
        if ((err as Error).name === "AbortError") return;
        if (err instanceof AuthExpiredError) return;
        setError(err instanceof Error ? err.message : "Ошибка при загрузке");
      } finally {
        setLoading(false);
      }
    };

    void fetchResult();
    return () => controller.abort();
  }, [resultId]);

  const recommendations = result?.recommendations ?? [];
  const topStrengths = result?.top_strengths ?? [];
  const confidenceScore = Math.round(Number((result?.confidence ?? {}).score ?? 0));

  const archetype = useMemo(() => {
    if (!result?.profile_scores) return "Профиль учащегося";
    return deriveArchetype(result.profile_scores);
  }, [result?.profile_scores]);

  const topDimensions = useMemo(() => {
    if (!result?.profile_scores) return [];
    return Object.entries(result.profile_scores)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([dim]) => dim);
  }, [result?.profile_scores]);

  const toggleFavorite = (slug: string) => {
    setFavorites((prev) => ({ ...prev, [slug]: !prev[slug] }));
  };

  return (
    <div className="results-page">
      <SiteHeader />

      <main className="results-content">
        <ProfileSummaryHero
          archetype={archetype}
          interests={topDimensions}
          strongSubjects={[]}
        />

        <div className="results-header">
          <span className="results-section-label">Результаты</span>
          <h1 className="results-heading">Результаты прохождения теста</h1>
          <p className="results-subheading">
            Сначала показан краткий обзор результата, затем список рекомендаций по профессиям.
          </p>
        </div>

        {loading && <div className="loading-state">Загружаем результаты...</div>}
        {error && <div className="error-state">{error}</div>}

        {!loading && !error && recommendations.length === 0 && (
          <div className="empty-state">Рекомендации не найдены. Пройдите тест заново.</div>
        )}

        {recommendations.length > 0 && (
          <ExplanationPanel
            title="Краткий разбор результата"
            description="Сильные стороны и уверенность по результатам завершенного прохождения."
          >
            {topStrengths.length > 0 ? (
              topStrengths.slice(0, 4).map((item, idx) => (
                <ExplanationItem
                  key={`${item.title ?? "strength"}-${idx}`}
                  title={item.title ?? "Сильная сторона"}
                  description={strengthDescription(item)}
                  score={typeof item.score === "number" ? item.score : undefined}
                />
              ))
            ) : (
              <ExplanationItem
                title="Сильные стороны"
                description="Данные по сильным сторонам неполные для этого прохождения."
              />
            )}
            <ExplanationItem
              title="Уверенность результата"
              description={`Оценка confidence: ${confidenceScore || "н/д"}.`}
              score={confidenceScore || undefined}
            />
          </ExplanationPanel>
        )}

        {recommendations.length > 0 && (
          <div className="recommendations-grid">
            {recommendations.map((item, index) => {
              const title = item.profession ?? item.title ?? "Профессия";
              const score = Math.round(Number(item.score ?? item.match_score ?? 0));
              const description = item.why_fit ?? item.summary ?? (item.explanation ?? []).join(" ") ?? "";
              return (
                <RecommendationCard
                  key={item.slug}
                  rank={index + 1}
                  title={title}
                  slug={item.slug}
                  matchScore={score}
                  category={item.cluster}
                  description={description}
                  isFavorited={favorites[item.slug]}
                  onFavorite={() => toggleFavorite(item.slug)}
                />
              );
            })}
          </div>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
