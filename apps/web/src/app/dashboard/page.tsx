"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { RecommendationCard } from "@/components/layout/recommendation-card";
import { TabNav } from "@/components/layout/tab-nav";
import { SearchFilterBar } from "@/components/layout/search-filter-bar";
import { ResultsHistoryList } from "@/components/layout/results-history-list";
import { ResultDetailView } from "@/components/layout/result-detail-view";
import { getAccountEmail, getOnboardingProfile, type OnboardingProfile } from "@/lib/auth-flow";
import { authFetch, AuthExpiredError, trackTelemetryEvent } from "@/lib/api-client";

const AI_SESSION_KEY = "ai_assessment_session_id";

type TabId = "profile" | "results" | "favorites" | "settings";

type Recommendation = {
  profession: string;
  slug: string;
  score: number;
  rank: number;
  explanation: string[];
};

type ResultHistoryItem = {
  result_id: string;
  assessment_slug: string;
  test_title: string;
  completed_at: string;
  top_professions: string[];
  is_latest: boolean;
};

type ResultDetail = Record<string, unknown> & {
  result_id: string;
  assessment_slug: string;
  payload_version?: "express_result_v1" | "full_result_v1";
  recommendations?: Recommendation[];
  top_professions?: Array<{
    title: string;
    profession_slug: string;
    relevance_score: number;
    rank: number;
    why_fit: string;
  }>;
};

function recommendationFromResult(payload: ResultDetail | null): Recommendation[] {
  if (!payload) return [];

  if (payload.payload_version === "full_result_v1") {
    const rows = (payload.top_professions ?? []) as Array<{
      title: string;
      profession_slug: string;
      relevance_score: number;
      rank: number;
      why_fit: string;
    }>;
    return rows.map((item) => ({
      profession: item.title,
      slug: item.profession_slug,
      score: Math.round(item.relevance_score),
      rank: item.rank,
      explanation: [item.why_fit],
    }));
  }

  if (payload.payload_version === "express_result_v1") {
    return [];
  }

  return ((payload.recommendations ?? []) as Recommendation[]) ?? [];
}

function isDeepResult(payload: ResultDetail | null): boolean {
  return payload?.assessment_slug === "deep_v1";
}

async function emitCtaClicked(resultId: string, resultType: "express" | "full" | "legacy", targetAction: string, targetUrl: string | undefined, surface: "dashboard_history") {
  trackTelemetryEvent("cta_clicked", {
    result_id: resultId,
    result_type: resultType,
    target_action: targetAction,
    target_url_present: Boolean(targetUrl),
    surface,
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
        surface,
      }),
    });
  } catch {
    // non-blocking best effort
  }
}

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<TabId>("results");
  const [searchQuery, setSearchQuery] = useState("");
  const [favorites, setFavorites] = useState<Record<string, boolean>>({});
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState<OnboardingProfile | null>(null);

  const [resultsHistory, setResultsHistory] = useState<ResultHistoryItem[]>([]);
  const [selectedResultId, setSelectedResultId] = useState<string | null>(null);

  const [selectedResult, setSelectedResult] = useState<ResultDetail | null>(null);
  const [selectedLoading, setSelectedLoading] = useState(false);
  const [selectedError, setSelectedError] = useState<string | null>(null);
  const [hasAiSession, setHasAiSession] = useState(false);

  useEffect(() => {
    const localProfile = getOnboardingProfile();
    const accountEmail = getAccountEmail();
    if (localProfile) {
      setProfile({
        ...localProfile,
        email: localProfile.email || accountEmail,
      });
    } else {
      setProfile(null);
    }
    if (typeof window !== "undefined") {
      setHasAiSession(Boolean(localStorage.getItem(AI_SESSION_KEY)));
    }

    const loadBackendProfile = async () => {
      try {
        const res = await authFetch("/profile/me");
        if (!res.ok) return;
        const backend = await res.json();

        const fullName = String(backend.full_name ?? "").trim();
        const parts = fullName ? fullName.split(/\s+/) : [];
        const mapped: OnboardingProfile = {
          surname: parts[0] ?? localProfile?.surname ?? "",
          name: parts[1] ?? localProfile?.name ?? "",
          patronymic: parts.slice(2).join(" ") || localProfile?.patronymic || "",
          age: backend.birth_date ? Number(backend.birth_date) || localProfile?.age || null : localProfile?.age || null,
          gender: String(backend.gender ?? localProfile?.gender ?? "") as OnboardingProfile["gender"],
          school: String(backend.school ?? backend.city ?? localProfile?.school ?? ""),
          grade: Number(backend.grades?.class_grade ?? localProfile?.grade ?? 0) || null,
          phone: String(backend.phone ?? localProfile?.phone ?? ""),
          email: String(localProfile?.email || accountEmail || ""),
          completedAt: localProfile?.completedAt || null,
        };
        setProfile(mapped);
      } catch {
        // fallback stays localStorage-based
      }
    };

    void loadBackendProfile();
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    const fetchRecommendations = async () => {
      if (activeTab !== "results" && activeTab !== "favorites") {
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const historyRes = await authFetch("/assessments/results/history", {
          signal: controller.signal,
        });
        if (!historyRes.ok) {
          throw new Error("Не удалось загрузить историю результатов");
        }
        const historyPayload = (await historyRes.json()) as { items?: ResultHistoryItem[] };
        const items = historyPayload.items ?? [];
        setResultsHistory(items);

        if (items.length === 0) {
          setRecommendations([]);
          setSelectedResultId(null);
          setSelectedResult(null);
          return;
        }

        const initialId = items[0].result_id;
        setSelectedResultId((prev) => prev ?? initialId);
      } catch (err) {
        const isAbort =
          controller.signal.aborted ||
          (err instanceof Error &&
            (err.name === "AbortError" ||
              err.message.includes("signal is aborted") ||
              err.message.includes("aborted")));

        if (isAbort) return;
        if (err instanceof AuthExpiredError) return;
        setError(err instanceof Error ? err.message : "Ошибка при загрузке");
      } finally {
        setLoading(false);
      }
    };

    void fetchRecommendations();

    return () => controller.abort();
  }, [activeTab]);

  useEffect(() => {
    const controller = new AbortController();

    const loadSelectedResult = async () => {
      if (activeTab !== "results" || !selectedResultId) {
        return;
      }
      setSelectedLoading(true);
      setSelectedError(null);
      try {
        let payload: ResultDetail | null = null;

        const fullResponse = await authFetch(`/assessments/results/${selectedResultId}/full`, {
          signal: controller.signal,
        });
        if (fullResponse.ok) {
          payload = (await fullResponse.json()) as ResultDetail;
          trackTelemetryEvent("history_payload_type_loaded", {
            result_id: selectedResultId,
            payload_type: "full_result_v1",
            surface: "dashboard_history",
          });
        }

        if (!isDeepResult(payload)) {
          const expressResponse = await authFetch(`/assessments/results/${selectedResultId}/express`, {
            signal: controller.signal,
          });
          if (expressResponse.ok) {
            payload = (await expressResponse.json()) as ResultDetail;
            trackTelemetryEvent("history_payload_type_loaded", {
              result_id: selectedResultId,
              payload_type: "express_result_v1",
              surface: "dashboard_history",
            });
          }
        }

        if (!payload) {
          const legacyResponse = await authFetch(`/assessments/results/${selectedResultId}`, {
            signal: controller.signal,
          });
          if (!legacyResponse.ok) {
            if (legacyResponse.status === 404) {
              throw new Error("Результат не найден или недоступен");
            }
            throw new Error("Не удалось загрузить выбранный результат");
          }
          payload = (await legacyResponse.json()) as ResultDetail;
          trackTelemetryEvent("history_payload_type_loaded", {
            result_id: selectedResultId,
            payload_type: "legacy",
            surface: "dashboard_history",
          });
        }

        setSelectedResult(payload);
        setRecommendations(recommendationFromResult(payload));
      } catch (err) {
        const isAbort =
          controller.signal.aborted ||
          (err instanceof Error &&
            (err.name === "AbortError" || err.message.includes("aborted")));
        if (isAbort) return;
        if (err instanceof AuthExpiredError) return;
        setSelectedResult(null);
        setSelectedError(err instanceof Error ? err.message : "Ошибка загрузки результата");
      } finally {
        setSelectedLoading(false);
      }
    };

    void loadSelectedResult();
    return () => controller.abort();
  }, [activeTab, selectedResultId]);

  const toggleFavorite = (slug: string) => {
    setFavorites((prev) => ({
      ...prev,
      [slug]: !prev[slug],
    }));
  };

  const filteredRecommendations = recommendations.filter((rec) =>
    (rec.profession ?? "").toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case "profile":
        return (
          <div className="dashboard-tab-content">
            <div className="settings-section">
              <div className="settings-card">
                <div className="flex items-center justify-between gap-4 mb-4">
                  <h2 className="dashboard-section-heading">Личные данные</h2>
                  <Link href="/onboarding" className="header-btn header-btn-ghost">Редактировать</Link>
                </div>

                {profile ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <p><strong>Фамилия:</strong> {profile.surname || "—"}</p>
                    <p><strong>Имя:</strong> {profile.name || "—"}</p>
                    <p><strong>Отчество:</strong> {profile.patronymic || "—"}</p>
                    <p><strong>Возраст:</strong> {profile.age ?? "—"}</p>
                    <p><strong>Пол:</strong> {profile.gender === "male" ? "Муж" : profile.gender === "female" ? "Жен" : "—"}</p>
                    <p><strong>Школа:</strong> {profile.school || "—"}</p>
                    <p><strong>Класс:</strong> {profile.grade ?? "—"}</p>
                    <p><strong>Контактный номер телефона:</strong> {profile.phone || "—"}</p>
                    <p className="md:col-span-2"><strong>Email:</strong> {profile.email || "—"}</p>
                  </div>
                ) : (
                  <p className="settings-placeholder">Профиль ещё не заполнен. Нажмите «Редактировать», чтобы добавить данные.</p>
                )}
              </div>

              <div className="settings-card mt-4">
                <h2 className="dashboard-section-heading">Результаты и предпочтения</h2>
                {recommendations.length > 0 ? (
                  <div className="text-sm space-y-2 mt-3">
                    <p><strong>Рекомендаций получено:</strong> {recommendations.length}</p>
                    <p><strong>Топ рекомендация:</strong> {recommendations[0]?.profession ?? "—"}</p>
                    <p><strong>Избранное:</strong> {Object.values(favorites).filter(Boolean).length}</p>
                  </div>
                ) : (
                  <p className="settings-placeholder">Результаты, интересы и достижения появятся после прохождения теста.</p>
                )}
              </div>
            </div>
          </div>
        );

      case "results":
        return (
          <div className="dashboard-tab-content">
            <div className="grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-4">
              <div>
                {loading && <div className="loading-state">Загружаем историю результатов...</div>}
                {error && <div className="error-state">{error}</div>}
                {!loading && !error && resultsHistory.length === 0 && (
                  <div className="empty-state">У вас пока нет завершенных прохождений теста.</div>
                )}
                {!loading && !error && resultsHistory.length > 0 && (
                  <ResultsHistoryList
                    items={resultsHistory}
                    selectedResultId={selectedResultId}
                    onSelect={setSelectedResultId}
                  />
                )}
              </div>

              <div>
                <ResultDetailView
                  detail={selectedResult ? { ...selectedResult, recommendations: filteredRecommendations } : null}
                  loading={selectedLoading}
                  error={selectedError}
                  favorites={favorites}
                  onToggleFavorite={toggleFavorite}
                  onCtaClicked={({ resultId, resultType, targetAction, targetUrl, surface }) => {
                    void emitCtaClicked(resultId, resultType, targetAction, targetUrl, surface);
                  }}
                />
                <SearchFilterBar value={searchQuery} onChange={setSearchQuery} />
              </div>
            </div>
          </div>
        );

      case "favorites": {
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
      }

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
          <div className="mt-3 flex flex-wrap gap-2">
            <Link href="/ai-assessment" className="header-btn header-btn-primary">
              Определить профессию с AI
            </Link>
            {hasAiSession && (
              <Link href="/ai-assessment" className="header-btn header-btn-ghost">
                Продолжить AI-диалог
              </Link>
            )}
          </div>
        </div>

        <TabNav activeTab={activeTab} onTabChange={setActiveTab} />

        {renderTabContent()}
      </main>

      <SiteFooter />
    </div>
  );
}
