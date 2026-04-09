"use client";

import { useEffect, useState } from "react";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { ProfileSummaryHero } from "@/components/layout/profile-summary-hero";
import { RecommendationCard } from "@/components/layout/recommendation-card";
import { ExplanationPanel } from "@/components/layout/explanation-panel";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

type Recommendation = {
  profession: string;
  slug: string;
  score: number;
  rank: number;
  explanation: string[];
};

type FavoritesState = Record<string, boolean>;

export default function ResultsPage() {
  const [results, setResults] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [favorites, setFavorites] = useState<FavoritesState>({});

  useEffect(() => {
    const controller = new AbortController();

    const fetchRecommendations = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${apiUrl}/recommendations`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          signal: controller.signal,
          body: JSON.stringify({
            user_id: "anon",
            vector: { analytical: 0.8, creative: 0.4, social: 0.6 },
            interests: ["it", "design"],
          }),
        });
        if (!response.ok) {
          throw new Error("Не удалось получить рекомендации");
        }
        const payload = await response.json();
        setResults(payload.recommendations ?? []);
      } catch (err) {
        if ((err as Error).name === "AbortError") {
          return;
        }
        setError(err instanceof Error ? err.message : "Ошибка при загрузке");
      } finally {
        setLoading(false);
      }
    };

    void fetchRecommendations();

    return () => controller.abort();
  }, []);

  const toggleFavorite = (slug: string) => {
    setFavorites((prev) => ({
      ...prev,
      [slug]: !prev[slug],
    }));
  };

  return (
    <div className="results-page">
      <SiteHeader />

      <main className="results-content">
        <ProfileSummaryHero
          archetype="Аналитик"
          grade="10 класс"
          interests={["Технологии", "Решение задач", "Проектирование"]}
          strongSubjects={["Математика", "Физика", "Информатика"]}
        />

        <div className="results-header">
          <span className="results-section-label">Результаты</span>
          <h1 className="results-heading">Персональные рекомендации</h1>
          <p className="results-subheading">
            Сформированы на основе официального вектора и сохранённых предпочтений.
            Каждый результат содержит объяснение и конкретные шаги.
          </p>
        </div>

        {loading && (
          <div className="loading-state">
            Загружаем рекомендации...
          </div>
        )}

        {error && (
          <div className="error-state">
            {error}
          </div>
        )}

        {results.length === 0 && !loading && !error && (
          <div className="empty-state">
            Рекомендации появятся после прохождения теста.
          </div>
        )}

        {results.length > 0 && (
          <div className="recommendations-grid">
            {results.map((item) => (
              <RecommendationCard
                key={item.slug}
                rank={item.rank}
                title={item.profession}
                slug={item.slug}
                matchScore={item.score}
                description={item.explanation.join(" ")}
                isFavorited={favorites[item.slug]}
                onFavorite={() => toggleFavorite(item.slug)}
              />
            ))}
          </div>
        )}

        {results.length > 0 && (
          <ExplanationPanel
            title="Почему эти профессии?"
            description="Мы анализируем несколько факторов, чтобы дать вам объяснимые рекомендации."
          />
        )}
      </main>

      <SiteFooter />
    </div>
  );
}