"use client";

import { useEffect, useState } from "react";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { ProfileSummaryHero } from "@/components/layout/profile-summary-hero";
import { RecommendationCard } from "@/components/layout/recommendation-card";
import { TabNav } from "@/components/layout/tab-nav";
import { SearchFilterBar } from "@/components/layout/search-filter-bar";
import { ExplanationPanel } from "@/components/layout/explanation-panel";

type TabId = "profile" | "results" | "favorites" | "settings";

type Recommendation = {
  profession: string;
  slug: string;
  score: number;
  rank: number;
  explanation: string[];
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<TabId>("results");
  const [searchQuery, setSearchQuery] = useState("");
  const [favorites, setFavorites] = useState<Record<string, boolean>>({});
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    const fetchRecommendations = async () => {
      if (activeTab !== "results" && activeTab !== "favorites") {
        return;
      }

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
        setRecommendations(payload.recommendations ?? []);
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
  }, [activeTab]);

  const toggleFavorite = (slug: string) => {
    setFavorites((prev) => ({
      ...prev,
      [slug]: !prev[slug],
    }));
  };

  const filteredRecommendations = recommendations.filter((rec) =>
    rec.profession.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case "profile":
        return (
          <div className="dashboard-tab-content">
            <div className="profile-section">
              <ProfileSummaryHero
                archetype="Аналитик"
                grade="10 класс"
                interests={["Технологии", "Решение задач", "Проектирование"]}
                strongSubjects={["Математика", "Физика", "Информатика"]}
              />
            </div>
          </div>
        );

      case "results":
        return (
          <div className="dashboard-tab-content">
            <SearchFilterBar
              value={searchQuery}
              onChange={setSearchQuery}
            />

            <h2 className="dashboard-section-heading">Ваши рекомендации</h2>

            {loading && (
              <div className="loading-state">Загружаем рекомендации...</div>
            )}

            {error && (
              <div className="error-state">{error}</div>
            )}

            {!loading && !error && filteredRecommendations.length > 0 && (
              <>
                <div className="recommendations-grid">
                  {filteredRecommendations.map((rec) => (
                    <RecommendationCard
                      key={rec.slug}
                      rank={rec.rank}
                      title={rec.profession}
                      slug={rec.slug}
                      matchScore={rec.score}
                      description={rec.explanation.join(" ")}
                      isFavorited={favorites[rec.slug]}
                      onFavorite={() => toggleFavorite(rec.slug)}
                    />
                  ))}
                </div>

                <ExplanationPanel
                  title="Как формируются рекомендации?"
                  description="Мы анализируем ваш профиль, результаты теста и интересы."
                />
              </>
            )}

            {!loading && !error && filteredRecommendations.length === 0 && (
              <div className="empty-state">
                Рекомендации появятся после прохождения теста.
              </div>
            )}
          </div>
        );

      case "favorites":
        const favoritedRecs = recommendations.filter((rec) => favorites[rec.slug]);

        return (
          <div className="dashboard-tab-content">
            <h2 className="dashboard-section-heading">Избранное</h2>

            {favoritedRecs.length > 0 ? (
              <div className="recommendations-grid">
                {favoritedRecs.map((rec) => (
                  <RecommendationCard
                    key={rec.slug}
                    rank={rec.rank}
                    title={rec.profession}
                    slug={rec.slug}
                    matchScore={rec.score}
                    description={rec.explanation.join(" ")}
                    isFavorited={true}
                    onFavorite={() => toggleFavorite(rec.slug)}
                  />
                ))}
              </div>
            ) : (
              <div className="empty-state">
                Сохраняйте интересные профессии, нажимая на сердечко.
              </div>
            )}
          </div>
        );

      case "settings":
        return (
          <div className="dashboard-tab-content">
            <div className="settings-section">
              <h2 className="dashboard-section-heading">Настройки аккаунта</h2>
              <div className="settings-card">
                <p className="settings-placeholder">
                  Настройки аккаунта будут доступны после регистрации.
                </p>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="dashboard-page">
      <SiteHeader />

      <main className="dashboard-content">
        <div className="dashboard-header">
          <h1 className="dashboard-title">Личный кабинет</h1>
          <p className="dashboard-subtitle">
            Следите за прохождением теста, сохраненными профессиями и рекомендациями.
          </p>
        </div>

        <TabNav activeTab={activeTab} onTabChange={setActiveTab} />

        {renderTabContent()}
      </main>

      <SiteFooter />
    </div>
  );
}