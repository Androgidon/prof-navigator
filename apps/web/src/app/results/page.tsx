"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { ProfileSummaryHero } from "@/components/layout/profile-summary-hero";
import { RecommendationCard } from "@/components/layout/recommendation-card";
import { ExplanationPanel, ExplanationItem } from "@/components/layout/explanation-panel";
import { authFetch, AuthExpiredError, trackTelemetryEvent } from "@/lib/api-client";

type LegacyRecommendation = {
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

type LegacyResultPayload = {
  result_id: string;
  assessment_slug: string;
  profile_scores: Record<string, number>;
  top_strengths?: Array<{ title?: string; description?: string; summary?: string; dimension?: string; score?: number }>;
  recommendations: LegacyRecommendation[];
  confidence: Record<string, unknown>;
};

type ExpressResultPayload = {
  result_id: string;
  assessment_slug: string;
  payload_version: "express_result_v1";
  profile_type: { primary_family: string; secondary_modifier?: string; summary: string };
  top_strengths: Array<{ dimension: string; score: number; explanation: string }>;
  top_directions: Array<{
    rank: number;
    title: string;
    fit_band: "high" | "medium";
    why_direction: string;
    example_professions: Array<{ profession_slug: string; title: string; family_title: string }>;
  }>;
  confidence: { score: number; level: "low" | "medium" | "high"; user_message: string };
  monetization_cta: { target_action: string; target_url?: string; title: string; text: string };
};

type FullResultPayload = {
  result_id: string;
  assessment_slug: string;
  payload_version: "full_result_v1";
  profile_type: { primary_family: string; secondary_modifier?: string; summary: string };
  top_strengths: Array<{ dimension: string; score: number; explanation?: string; evidence?: string }>;
  top_professions: Array<{
    rank: number;
    profession_slug: string;
    title: string;
    relevance_score: number;
    family_title: string;
    why_fit: string;
  }>;
  alternatives: Array<{
    pivot_type: string;
    title: string;
    explanation: string;
    professions: Array<{ profession_slug: string; title: string; reason: string }>;
  }>;
  overall_confidence: { score: number; level: "low" | "medium" | "high" };
};

type ResultPayload = LegacyResultPayload | ExpressResultPayload | FullResultPayload;

const DIMENSION_LABELS_RU: Record<string, string> = {
  analytical: "Аналитическое мышление",
  technical: "Техническое мышление",
  creative: "Креативность",
  social: "Коммуникация",
  helping: "Поддержка людей",
  leadership: "Лидерство",
  structured: "Системность",
  exploratory: "Исследовательский подход",
  detail: "Внимание к деталям",
  verbal: "Работа со словом",
  quantitative: "Количественное мышление",
  quantative: "Количественное мышление",
  practical: "Практичность",
};

function toReadableDimensionLabel(value?: string): string {
  if (!value) return "Сильная сторона";
  return DIMENSION_LABELS_RU[value] ?? value;
}

function isDeepAssessment(payload: { assessment_slug?: string } | null): boolean {
  return payload?.assessment_slug === "deep_v1";
}

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

function ctaLabel(targetAction: string): string {
  if (targetAction === "start_full_test") return "Пройти Full тест";
  if (targetAction === "compare_paths") return "Сравнить траектории";
  return "Открыть Full возможности";
}

async function emitCtaClicked(resultId: string, resultType: "express" | "full" | "legacy", targetAction: string, targetUrl?: string) {
  trackTelemetryEvent("cta_clicked", {
    result_id: resultId,
    result_type: resultType,
    target_action: targetAction,
    target_url_present: Boolean(targetUrl),
    surface: "results_page",
  });

  try {
    await authFetch(`/assessments/results/${resultId}/cta-clicked`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        result_id: resultId,
        result_type: resultType,
        target_action: targetAction,
        target_url_present: Boolean(targetUrl),
        surface: "results_page",
      }),
    });
  } catch {
    // non-blocking best effort
  }
}

export default function ResultsPage() {
  const searchParams = useSearchParams();
  const resultId = searchParams.get("result_id");

  const [result, setResult] = useState<ResultPayload | null>(null);
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
        const fullResponse = await authFetch(`/assessments/results/${resultId}/full`, {
          method: "GET",
          signal: controller.signal,
        });
        if (fullResponse.ok) {
          const fullPayload = (await fullResponse.json()) as FullResultPayload;
          setResult(fullPayload);
          if (isDeepAssessment(fullPayload)) {
            return;
          }
        }

        const expressResponse = await authFetch(`/assessments/results/${resultId}/express`, {
          method: "GET",
          signal: controller.signal,
        });

        if (expressResponse.ok) {
          setResult((await expressResponse.json()) as ExpressResultPayload);
          return;
        }

        const legacyResponse = await authFetch(`/assessments/results/${resultId}`, {
          method: "GET",
          signal: controller.signal,
        });
        if (!legacyResponse.ok) {
          if (legacyResponse.status === 404) throw new Error("Результат не найден или недоступен");
          throw new Error("Не удалось получить результаты теста");
        }
        setResult((await legacyResponse.json()) as LegacyResultPayload);
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

  const archetype = useMemo(() => {
    if (!result) return "Профиль учащегося";
    if ((result as ExpressResultPayload).payload_version === "express_result_v1") {
      return (result as ExpressResultPayload).profile_type.primary_family;
    }
    if ((result as FullResultPayload).payload_version === "full_result_v1") {
      return (result as FullResultPayload).profile_type.primary_family;
    }
    return deriveArchetype((result as LegacyResultPayload).profile_scores ?? {});
  }, [result]);

  const toggleFavorite = (slug: string) => {
    setFavorites((prev) => ({ ...prev, [slug]: !prev[slug] }));
  };

  return (
    <div className="results-page">
      <SiteHeader />

      <main className="results-content">
        <ProfileSummaryHero archetype={archetype} interests={[]} strongSubjects={[]} />

        <div className="results-header">
          <span className="results-section-label">Результаты</span>
          <h1 className="results-heading">Результаты прохождения теста</h1>
          <p className="results-subheading">
            Express показывает профиль и направления, Full — точный Top-8 профессий и персональные рекомендации.
          </p>
        </div>

        {loading && <div className="loading-state">Загружаем результаты...</div>}
        {error && <div className="error-state">{error}</div>}

        {!loading && !error && result && (result as ExpressResultPayload).payload_version === "express_result_v1" && (() => {
          const express = result as ExpressResultPayload;
          return (
            <>
              <ExplanationPanel title="Краткий разбор результата" description={express.profile_type.summary}>
                {express.top_strengths.slice(0, 4).map((item, idx) => (
                    <ExplanationItem
                      key={`${item.dimension}-${idx}`}
                      title={toReadableDimensionLabel(item.dimension)}
                      description={item.explanation}
                      score={item.score}
                    />

                ))}
                <ExplanationItem
                  title="Уверенность результата"
                  description={express.confidence.user_message}
                  score={Math.round(express.confidence.score)}
                />
              </ExplanationPanel>

              <h2 className="dashboard-section-heading">Топ направлений</h2>
              <div className="recommendations-grid">
                {express.top_directions.map((direction) => (
                  <article key={`${direction.title}-${direction.rank}`} className="recommendation-card">
                    <div className="card-header">
                      <span className="card-rank">#{direction.rank}</span>
                      <div className="card-badges">
                        <span className="category-chip">{direction.title}</span>
                        <span className="match-badge match-good">
                          {direction.fit_band === "high" ? "Высокое" : "Среднее"}
                        </span>
                      </div>
                    </div>
                    <p className="card-description">{direction.why_direction}</p>
                    <div className="card-tags">
                      {direction.example_professions.slice(0, 5).map((item) => (
                        <span key={`${item.profession_slug}-${item.title}`} className="tag-chip tag-subject">
                          {item.title}
                        </span>
                      ))}
                    </div>
                  </article>
                ))}
              </div>

              <div className="settings-card" style={{ marginTop: "1rem" }}>
                <h3 className="dashboard-section-heading" style={{ marginBottom: "0.5rem" }}>
                  {express.monetization_cta.title}
                </h3>
                <p className="admin-help" style={{ marginBottom: "0.75rem" }}>{express.monetization_cta.text}</p>
                <Link
                  href={express.monetization_cta.target_url || "/full-test"}
                  className="header-btn header-btn-primary"
                  onClick={() => {
                    void emitCtaClicked(
                      express.result_id,
                      "express",
                      express.monetization_cta.target_action,
                      express.monetization_cta.target_url
                    );
                  }}
                >
                  {ctaLabel(express.monetization_cta.target_action)}
                </Link>
              </div>
            </>
          );
        })()}

        {!loading && !error && result && (result as FullResultPayload).payload_version === "full_result_v1" && (() => {
          const full = result as FullResultPayload;
          return (
            <>
              <ExplanationPanel title="Краткий разбор результата" description={full.profile_type.summary}>
                {full.top_strengths.slice(0, 4).map((item, idx) => (
                    <ExplanationItem
                      key={`${item.dimension}-${idx}`}
                      title={toReadableDimensionLabel(item.dimension)}
                      description={item.explanation ?? item.evidence ?? "Сильная сторона по результатам теста."}
                      score={item.score}
                    />

                ))}
                <ExplanationItem
                  title="Уверенность результата"
                  description={`Уровень: ${full.overall_confidence.level}.`}
                  score={Math.round(full.overall_confidence.score)}
                />
              </ExplanationPanel>

              <h2 className="dashboard-section-heading">Top-8 профессий</h2>
              {full.top_professions.length > 0 ? (
                <div className="recommendations-grid">
                  {full.top_professions.map((rec) => (
                    <RecommendationCard
                      key={rec.profession_slug}
                      rank={rec.rank}
                      title={rec.title}
                      slug={rec.profession_slug}
                      matchScore={Math.round(rec.relevance_score)}
                      category={rec.family_title}
                      description={rec.why_fit}
                      isFavorited={favorites[rec.profession_slug]}
                      onFavorite={() => toggleFavorite(rec.profession_slug)}
                    />
                  ))}
                </div>
              ) : (
                <div className="empty-state">Профессии пока недоступны для этого результата.</div>
              )}
            </>
          );
        })()}

        {!loading && !error && result && !("payload_version" in result) && (() => {
          const legacy = result as LegacyResultPayload;
          const recommendations = legacy.recommendations ?? [];
          const topStrengths = legacy.top_strengths ?? [];
          const confidenceScore = Math.round(Number((legacy.confidence ?? {}).score ?? 0));

          return (
            <>
              {recommendations.length > 0 && (
                <ExplanationPanel
                  title="Краткий разбор результата"
                  description="Сильные стороны и уверенность по результатам завершенного прохождения."
                >
                  {topStrengths.slice(0, 4).map((item, idx) => (
                    <ExplanationItem
                      key={`${item.title ?? "strength"}-${idx}`}
                      title={item.title ?? item.dimension ?? "Сильная сторона"}
                      description={item.description ?? item.summary ?? "Сильная сторона по результатам теста."}
                      score={typeof item.score === "number" ? item.score : undefined}
                    />
                  ))}
                  <ExplanationItem
                    title="Уверенность результата"
                    description={`Оценка confidence: ${confidenceScore || "н/д"}.`}
                    score={confidenceScore || undefined}
                  />
                </ExplanationPanel>
              )}

              {recommendations.length > 0 ? (
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
              ) : (
                <div className="empty-state">Рекомендации не найдены. Пройдите тест заново.</div>
              )}
            </>
          );
        })()}
      </main>

      <SiteFooter />
    </div>
  );
}
