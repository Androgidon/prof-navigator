"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { SearchFilterBar } from "@/components/layout/search-filter-bar";
import { cn } from "@/lib/utils";

type ProfessionListItem = {
  slug: string;
  title: string;
  cluster: string;
  summary: string;
  status: string;
};

type ViewMode = "grid" | "list";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

function normalizeSummary(summary: string): string {
  const value = summary?.trim();
  if (!value) {
    return "Краткое описание пока дополняется редакцией каталога.";
  }
  return value;
}

export default function ProfessionsPage() {
  const [professions, setProfessions] = useState<ProfessionListItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCluster, setSelectedCluster] = useState<string>("Все");
  const [viewMode, setViewMode] = useState<ViewMode>("grid");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    const fetchProfessions = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${apiUrl}/professions/`, {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error("Не удалось загрузить каталог профессий");
        }
        const data = (await response.json()) as ProfessionListItem[];
        setProfessions(data.filter((item) => item.status === "active"));
      } catch (err) {
        if ((err as Error).name !== "AbortError") {
          setError(err instanceof Error ? err.message : "Ошибка при загрузке");
        }
      } finally {
        setLoading(false);
      }
    };

    void fetchProfessions();
    return () => controller.abort();
  }, []);

  const clusters = useMemo(() => {
    const unique = Array.from(new Set(professions.map((item) => item.cluster).filter(Boolean))).sort((a, b) =>
      a.localeCompare(b, "ru")
    );
    return ["Все", ...unique];
  }, [professions]);

  const clusterFiltered = useMemo(() => {
    if (selectedCluster === "Все") {
      return professions;
    }
    return professions.filter((profession) => profession.cluster === selectedCluster);
  }, [professions, selectedCluster]);

  const filteredProfessions = useMemo(() => {
    const normalizedQuery = searchQuery.trim().toLowerCase();
    if (!normalizedQuery) {
      return clusterFiltered;
    }

    return clusterFiltered.filter((profession) => {
      const inTitle = profession.title.toLowerCase().includes(normalizedQuery);
      const inCluster = profession.cluster.toLowerCase().includes(normalizedQuery);
      const inSummary = profession.summary.toLowerCase().includes(normalizedQuery);
      return inTitle || inCluster || inSummary;
    });
  }, [clusterFiltered, searchQuery]);

  const isSearchActive = searchQuery.trim().length > 0;

  return (
    <div className="professions-page">
      <SiteHeader />

      <main className="professions-content">
        <div className="professions-header">
          <h1 className="professions-title">Профессии</h1>
          <p className="professions-subtitle">
            Каталог активных профессий: выберите категорию, формат просмотра и откройте подробную страницу.
          </p>
        </div>

        <div className="professions-toolbar">
          <SearchFilterBar
            value={searchQuery}
            onChange={setSearchQuery}
            className="professions-search"
            showFilters={false}
          />

          <div className="view-mode-toggle" role="group" aria-label="Режим отображения">
            <button
              type="button"
              className={cn("view-mode-btn", viewMode === "grid" && "view-mode-btn-active")}
              onClick={() => setViewMode("grid")}
            >
              Плитка
            </button>
            <button
              type="button"
              className={cn("view-mode-btn", viewMode === "list" && "view-mode-btn-active")}
              onClick={() => setViewMode("list")}
            >
              Список
            </button>
          </div>
        </div>

        {!loading && !error && clusters.length > 1 && (
          <div className="category-nav" role="tablist" aria-label="Категории профессий">
            {clusters.map((cluster) => (
              <button
                key={cluster}
                type="button"
                role="tab"
                aria-selected={selectedCluster === cluster}
                className={cn("category-chip", selectedCluster === cluster && "category-chip-active")}
                onClick={() => setSelectedCluster(cluster)}
              >
                {cluster}
              </button>
            ))}
          </div>
        )}

        {loading && <div className="loading-state">Загружаем каталог профессий...</div>}
        {error && <div className="error-state">{error}</div>}

        {!loading && !error && professions.length === 0 && (
          <div className="empty-state">В каталоге пока нет активных профессий.</div>
        )}

        {!loading && !error && professions.length > 0 && clusterFiltered.length === 0 && (
          <div className="empty-state">В выбранной категории пока нет профессий.</div>
        )}

        {!loading && !error && professions.length > 0 && clusterFiltered.length > 0 && filteredProfessions.length === 0 && isSearchActive && (
          <div className="empty-state">По запросу ничего не найдено в выбранной категории.</div>
        )}

        {!loading && !error && filteredProfessions.length > 0 && (
          <div className={cn("professions-catalog", viewMode === "list" && "professions-catalog-list")}>
            {filteredProfessions.map((profession) => (
              <article key={profession.slug} className="profession-list-card">
                <div className="profession-list-card-head">
                  <h2>{profession.title}</h2>
                  <span>{profession.cluster}</span>
                </div>
                <p>{normalizeSummary(profession.summary)}</p>
                <div className="profession-list-card-actions">
                  <Link href={`/professions/${profession.slug}`} className="header-btn header-btn-ghost">
                    Подробнее
                  </Link>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>

      <SiteFooter />
    </div>
  );
}
