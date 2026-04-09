import { cn } from "@/lib/utils";

interface ProfileSummaryHeroProps {
  name?: string;
  archetype?: string;
  grade?: string;
  interests?: string[];
  strongSubjects?: string[];
  className?: string;
}

export function ProfileSummaryHero({
  name,
  archetype = "Аналитик",
  grade,
  interests = [],
  strongSubjects = [],
  className,
}: ProfileSummaryHeroProps) {
  return (
    <div className={cn("profile-summary-hero", className)}>
      <div className="profile-hero-content">
        <div className="profile-avatar">
          <span className="avatar-initial">
            {name ? name[0].toUpperCase() : "?"}
          </span>
        </div>
        <div className="profile-info">
          {name && <h1 className="profile-name">{name}</h1>}
          <div className="profile-meta">
            {archetype && (
              <span className="profile-archetype">{archetype}</span>
            )}
            {grade && (
              <span className="profile-grade">{grade}</span>
            )}
          </div>
          {interests.length > 0 && (
            <div className="profile-interests">
              {interests.map((interest) => (
                <span key={interest} className="interest-chip">
                  {interest}
                </span>
              ))}
            </div>
          )}
          {strongSubjects.length > 0 && (
            <div className="profile-subjects">
              <span className="subjects-label">Сильные предметы:</span>
              {strongSubjects.map((subject) => (
                <span key={subject} className="subject-chip">
                  {subject}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}