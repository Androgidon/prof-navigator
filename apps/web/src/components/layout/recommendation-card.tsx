import Link from "next/link";
import { cn } from "@/lib/utils";

interface RecommendationCardProps {
  rank: number;
  title: string;
  slug: string;
  matchScore: number;
  category?: string;
  description?: string;
  subjects?: string[];
  skills?: string[];
  salary?: string;
  onFavorite?: () => void;
  isFavorited?: boolean;
  className?: string;
}

function getMatchVariant(score: number): "match-excellent" | "match-good" | "match-moderate" | "match-low" {
  if (score >= 80) return "match-excellent";
  if (score >= 60) return "match-good";
  if (score >= 40) return "match-moderate";
  return "match-low";
}

function getMatchLabel(score: number): string {
  if (score >= 80) return "Отлично";
  if (score >= 60) return "Хорошо";
  if (score >= 40) return "Средне";
  return "Ниже среднего";
}

export function RecommendationCard({
  rank,
  title,
  slug,
  matchScore,
  category,
  description,
  subjects = [],
  skills = [],
  salary,
  onFavorite,
  isFavorited,
  className,
}: RecommendationCardProps) {
  const matchVariant = getMatchVariant(matchScore);
  const matchLabel = getMatchLabel(matchScore);

  return (
    <article className={cn("recommendation-card", className)}>
      <div className="card-header">
        <span className="card-rank">#{rank}</span>
        <div className="card-badges">
          {category && (
            <span className="category-chip">{category}</span>
          )}
          <span className={`match-badge ${matchVariant}`}>
            {matchScore}% • {matchLabel}
          </span>
        </div>
      </div>

      <h3 className="card-title">{title}</h3>

      {description && (
        <p className="card-description">{description}</p>
      )}

      <div className="card-tags">
        {subjects.map((subject) => (
          <span key={subject} className="tag-chip tag-subject">
            {subject}
          </span>
        ))}
        {skills.map((skill) => (
          <span key={skill} className="tag-chip tag-skill">
            {skill}
          </span>
        ))}
      </div>

      {salary && (
        <div className="card-salary">
          <span className="salary-label">Зарплата:</span>
          <span className="salary-value">{salary}</span>
        </div>
      )}

      <div className="card-actions">
        <button
          type="button"
          onClick={onFavorite}
          className={cn("favorite-btn", isFavorited && "favorite-btn-active")}
          aria-label={isFavorited ? "Удалить из избранного" : "Добавить в избранное"}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill={isFavorited ? "currentColor" : "none"}
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
          </svg>
        </button>
        <Link href={`/professions/${slug}`} className="details-btn">
          Подробнее →
        </Link>
      </div>
    </article>
  );
}