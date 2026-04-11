import Link from "next/link";
import { cn } from "@/lib/utils";

interface ProfessionHeroProps {
  title: string;
  category?: string;
  matchScore?: number;
  isFavorited?: boolean;
  onFavorite?: () => void;
  backHref?: string;
  backLabel?: string;
  className?: string;
}

function getMatchLabel(score: number): string {
  if (score >= 80) return "Отлично подходит";
  if (score >= 60) return "Хорошо подходит";
  if (score >= 40) return "Среднее соответствие";
  return "Ниже среднего";
}

export function ProfessionHero({
  title,
  category,
  matchScore,
  isFavorited,
  onFavorite,
  backHref = "/results",
  backLabel = "Назад к результатам",
  className,
}: ProfessionHeroProps) {
  return (
    <div className={cn("profession-hero", className)}>
      <Link href={backHref} className="back-link">
        ← {backLabel}
      </Link>

      <div className="hero-content">
        <div className="hero-badges">
          {category && (
            <span className="category-chip">{category}</span>
          )}
          {matchScore !== undefined && (
            <span className={`match-badge ${matchScore >= 60 ? "match-good" : "match-moderate"}`}>
              {matchScore}% — {getMatchLabel(matchScore)}
            </span>
          )}
        </div>

        <h1 className="hero-title">{title}</h1>

        {onFavorite && (
          <button
            type="button"
            onClick={onFavorite}
            className={cn("favorite-btn-lg", isFavorited && "favorite-btn-active")}
            aria-label={isFavorited ? "Удалить из избранного" : "Добавить в избранное"}
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill={isFavorited ? "currentColor" : "none"}
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
            </svg>
            <span>{isFavorited ? "В избранном" : "В избранное"}</span>
          </button>
        )}
      </div>
    </div>
  );
}