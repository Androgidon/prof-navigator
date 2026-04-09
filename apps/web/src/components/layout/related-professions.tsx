import Link from "next/link";
import { cn } from "@/lib/utils";

interface RelatedProfessionItemProps {
  title: string;
  slug: string;
  matchScore?: number;
  className?: string;
}

export function RelatedProfessionItem({
  title,
  slug,
  matchScore,
  className,
}: RelatedProfessionItemProps) {
  return (
    <Link href={`/professions/${slug}`} className={cn("related-profession-item", className)}>
      <div className="related-info">
        <h4 className="related-title">{title}</h4>
        {matchScore !== undefined && (
          <span className={`match-badge-sm ${matchScore >= 60 ? "match-good" : "match-moderate"}`}>
            {matchScore}%
          </span>
        )}
      </div>
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        className="related-arrow"
      >
        <path d="M5 12h14M12 5l7 7-7 7" />
      </svg>
    </Link>
  );
}

interface RelatedProfessionsProps {
  title?: string;
  items: { title: string; slug: string; matchScore?: number }[];
  className?: string;
}

export function RelatedProfessions({
  title = "Похожие профессии",
  items,
  className,
}: RelatedProfessionsProps) {
  return (
    <div className={cn("related-professions", className)}>
      <h3 className="related-professions-title">{title}</h3>
      <div className="related-list">
        {items.map((item) => (
          <RelatedProfessionItem
            key={item.slug}
            title={item.title}
            slug={item.slug}
            matchScore={item.matchScore}
          />
        ))}
      </div>
    </div>
  );
}