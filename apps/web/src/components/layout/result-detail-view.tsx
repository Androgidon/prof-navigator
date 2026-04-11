import { RecommendationCard } from "@/components/layout/recommendation-card";
import { ExplanationPanel, ExplanationItem } from "@/components/layout/explanation-panel";

type TopStrengthItem = {
  title?: string;
  description?: string;
  summary?: string;
  dimension?: string;
  score?: number;
};

type ResultDetail = {
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

type ResultDetailViewProps = {
  detail: ResultDetail | null;
  loading: boolean;
  error: string | null;
  favorites: Record<string, boolean>;
  onToggleFavorite: (slug: string) => void;
};

function strengthDescription(item: TopStrengthItem): string {
  if (item.description && item.description.trim().length > 0) return item.description;
  if (item.summary && item.summary.trim().length > 0) return item.summary;
  if (item.dimension && item.dimension.trim().length > 0) {
    return `Высокий показатель по направлению ${item.dimension}.`;
  }
  return "Сильная сторона по результатам выбранного прохождения теста.";
}

export function ResultDetailView({ detail, loading, error, favorites, onToggleFavorite }: ResultDetailViewProps) {
  if (loading) {
    return <div className="loading-state">Загрузка выбранного результата...</div>;
  }

  if (error) {
    return <div className="error-state">{error}</div>;
  }

  if (!detail) {
    return <div className="empty-state">Выберите прохождение из истории.</div>;
  }

  const recommendations = detail.recommendations ?? [];
  const topStrengths = detail.top_strengths ?? [];
  const confidenceScore = Number((detail.confidence ?? {}).score ?? 0);

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
