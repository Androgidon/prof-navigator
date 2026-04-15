import Link from "next/link";
import { RecommendationCard } from "@/components/layout/recommendation-card";
import { ExplanationPanel, ExplanationItem } from "@/components/layout/explanation-panel";

type TopStrengthItem = {
  title?: string;
  description?: string;
  summary?: string;
  dimension?: string;
  score?: number;
  explanation?: string;
};

type LegacyResultDetail = {
  result_id: string;
  assessment_slug: string;
  completed_at: string | null;
  profile_summary: Record<string, unknown>;
  top_strengths: TopStrengthItem[];
  work_style: Record<string, unknown>;
  recommendations: Array<{
    profession?: string;
    title?: string;
    slug?: string;
    score?: number;
    match_score?: number;
    rank?: number;
    explanation?: string[];
    why_fit?: string;
    summary?: string;
    cluster?: string;
  }>;
  next_steps: Record<string, unknown>;
  confidence: Record<string, unknown>;
  dimension_evidence: Record<string, unknown>;
};

type ExpressResultDetail = {
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
    example_professions: Array<{
      profession_slug: string;
      title: string;
      family_title: string;
    }>;
  }>;
  confidence: { score: number; level: "low" | "medium" | "high"; user_message: string };
  monetization_cta: { target_action: string; target_url?: string; title: string; text: string };
};

type FullResultDetail = {
  result_id: string;
  assessment_slug: string;
  payload_version: "full_result_v1";
  profile_type: { primary_family: string; secondary_modifier?: string; summary: string };
  top_strengths: Array<{ dimension: string; score: number; explanation?: string; evidence?: string }>;
  top_directions: Array<{ rank: number; title: string; why_direction: string }>;
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
  development_plan: { days_30: string[]; days_90: string[]; days_180: string[] };
  overall_confidence: { score: number; level: "low" | "medium" | "high" };
};

type ResultDetailViewProps = {
  detail: Record<string, unknown> | null;
  loading: boolean;
  error: string | null;
  favorites: Record<string, boolean>;
  onToggleFavorite: (slug: string) => void;
  onCtaClicked?: (params: { resultId: string; resultType: "express" | "full" | "legacy"; targetAction: string; targetUrl?: string; surface: "dashboard_history" }) => void;
};

function strengthDescription(item: TopStrengthItem): string {
  if (item.explanation && item.explanation.trim().length > 0) return item.explanation;
  if (item.description && item.description.trim().length > 0) return item.description;
  if (item.summary && item.summary.trim().length > 0) return item.summary;
  if (item.dimension && item.dimension.trim().length > 0) {
    return `Высокий показатель по направлению ${item.dimension}.`;
  }
  return "Сильная сторона по результатам выбранного прохождения теста.";
}

function ctaLabel(targetAction: string): string {
  if (targetAction === "start_full_test") return "Пройти Full тест";
  if (targetAction === "compare_paths") return "Сравнить траектории";
  return "Открыть Full возможности";
}

export function ResultDetailView({ detail, loading, error, favorites, onToggleFavorite, onCtaClicked }: ResultDetailViewProps) {
  if (loading) return <div className="loading-state">Загрузка выбранного результата...</div>;
  if (error) return <div className="error-state">{error}</div>;
  if (!detail) return <div className="empty-state">Выберите прохождение из истории.</div>;

  if ((detail as ExpressResultDetail).payload_version === "express_result_v1") {
    const express = detail as ExpressResultDetail;
    return (
      <div className="dashboard-tab-content">
        <ExplanationPanel
          title="Краткий разбор результата"
          description={express.profile_type.summary}
        >
          {express.top_strengths.slice(0, 4).map((item, idx) => (
            <ExplanationItem
              key={`${item.dimension}-${idx}`}
              title={item.dimension}
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

        <h2 className="dashboard-section-heading">Направления</h2>
        <div className="recommendations-grid">
          {express.top_directions.map((direction) => (
            <article key={`${direction.title}-${direction.rank}`} className="recommendation-card">
              <div className="card-header">
                <span className="card-rank">#{direction.rank}</span>
                <div className="card-badges">
                  <span className="category-chip">{direction.title}</span>
                  <span className="match-badge match-good">{direction.fit_band === "high" ? "Высокое" : "Среднее"}</span>
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
              onCtaClicked?.({
                resultId: express.result_id,
                resultType: "express",
                targetAction: express.monetization_cta.target_action,
                targetUrl: express.monetization_cta.target_url,
                surface: "dashboard_history",
              });
            }}
          >
            {ctaLabel(express.monetization_cta.target_action)}
          </Link>
        </div>
      </div>
    );
  }

  if ((detail as FullResultDetail).payload_version === "full_result_v1") {
    const full = detail as FullResultDetail;
    return (
      <div className="dashboard-tab-content">
        <ExplanationPanel
          title="Краткий разбор результата"
          description={full.profile_type.summary}
        >
          {full.top_strengths.slice(0, 4).map((item, idx) => (
            <ExplanationItem
              key={`${item.dimension}-${idx}`}
              title={item.dimension}
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
                isFavorited={Boolean(favorites[rec.profession_slug])}
                onFavorite={() => onToggleFavorite(rec.profession_slug)}
              />
            ))}
          </div>
        ) : (
          <div className="empty-state">Профессии пока не рассчитаны для этого прохождения.</div>
        )}

        {full.alternatives.length > 0 && (
          <div className="settings-card" style={{ marginTop: "1rem" }}>
            <h3 className="dashboard-section-heading">Альтернативные траектории</h3>
            {full.alternatives.map((alt) => (
              <div key={alt.pivot_type} style={{ marginTop: "0.75rem" }}>
                <strong>{alt.title}</strong>
                <p className="admin-help">{alt.explanation}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  const legacy = detail as LegacyResultDetail;
  const recommendations = legacy.recommendations ?? [];
  const topStrengths = legacy.top_strengths ?? [];
  const confidenceScore = Number((legacy.confidence ?? {}).score ?? 0);

  return (
    <div className="dashboard-tab-content">
      <ExplanationPanel
        title="Краткий разбор результата"
        description="Сильные стороны, стиль работы и уверенность для выбранного прохождения."
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
          <ExplanationItem title="Сильные стороны" description="Данные по сильным сторонам неполные для этого прохождения." />
        )}

        <ExplanationItem
          title="Уверенность результата"
          description={`Оценка confidence: ${confidenceScore || "н/д"}.`}
          score={confidenceScore || undefined}
        />
      </ExplanationPanel>

      <h2 className="dashboard-section-heading">Рекомендации</h2>

      {recommendations.length > 0 ? (
        <div className="recommendations-grid">
          {recommendations.map((rec, idx) => {
            const title = rec.profession ?? rec.title ?? "Профессия";
            const matchScore = Math.round(Number(rec.score ?? rec.match_score ?? 0));
            const description = rec.why_fit ?? rec.summary ?? (rec.explanation ?? []).join(" ");
            const slug = rec.slug ?? "";
            return (
              <RecommendationCard
                key={`${slug || "unknown"}-${idx}`}
                rank={rec.rank ?? idx + 1}
                title={title}
                slug={slug}
                matchScore={matchScore}
                category={rec.cluster}
                description={description}
                isFavorited={Boolean(slug && favorites[slug])}
                onFavorite={() => {
                  if (slug) onToggleFavorite(slug);
                }}
              />
            );
          })}
        </div>
      ) : (
        <div className="empty-state">В этом прохождении нет рекомендаций.</div>
      )}
    </div>
  );
}
