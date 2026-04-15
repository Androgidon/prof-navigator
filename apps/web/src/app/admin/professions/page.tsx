"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { StatusBadge } from "@/components/admin/status-badge";
import { adminFetch } from "@/lib/admin-api";
import { authFetch } from "@/lib/api-client";

type ProfessionRow = {
  slug: string;
  title: string;
  cluster: string;
  status: string;
  completeness_score: number;
};

type ProfessionListPageResponse = {
  items: ProfessionRow[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

type ProfessionListApiResponse = ProfessionListPageResponse | ProfessionRow[];

export default function ProfessionsListPage() {
  const [rows, setRows] = useState<ProfessionRow[]>([]);
  const [total, setTotal] = useState(0);
  const [q, setQ] = useState("");
  const [cluster, setCluster] = useState("");
  const [status, setStatus] = useState("");
  const [family, setFamily] = useState("");
  const [contentStatus, setContentStatus] = useState("");
  const [pageSize, setPageSize] = useState(20);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [legacyArrayMode, setLegacyArrayMode] = useState(false);

  const clusterOptions = useMemo(() => {
    const values = new Set<string>();
    for (const row of rows) {
      if (row.cluster.trim()) values.add(row.cluster.trim());
    }
    return Array.from(values).sort((a, b) => a.localeCompare(b, "ru"));
  }, [rows]);

  const activeCount = useMemo(() => rows.filter((row) => row.status.trim().toLowerCase() === "active").length, [rows]);
  const inactiveCount = useMemo(() => rows.length - activeCount, [rows, activeCount]);

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / pageSize)), [total, pageSize]);
  const visiblePages = useMemo(() => {
    if (totalPages <= 7) {
      return Array.from({ length: totalPages }, (_, index) => index + 1);
    }

    if (page <= 2) {
      return [1, 2, 3, "ellipsis-right", totalPages] as const;
    }

    if (page === 3) {
      return [1, 2, 3, 4, "ellipsis-right", totalPages] as const;
    }

    if (page >= totalPages - 1) {
      return [1, "ellipsis-left", totalPages - 2, totalPages - 1, totalPages] as const;
    }

    if (page === totalPages - 2) {
      return [1, "ellipsis-left", totalPages - 3, totalPages - 2, totalPages - 1, totalPages] as const;
    }

    return [1, "ellipsis-left", page - 1, page, page + 1, "ellipsis-right", totalPages] as const;
  }, [page, totalPages]);
  const paginatedRows = useMemo(() => {
    if (!legacyArrayMode) {
      return rows;
    }
    const start = (page - 1) * pageSize;
    return rows.slice(start, start + pageSize);
  }, [legacyArrayMode, rows, page, pageSize]);

  const filtersQueryString = useMemo(() => {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (cluster) params.set("cluster", cluster);
    if (status) params.set("status", status);
    if (family) params.set("family", family);
    if (contentStatus) params.set("content_status", contentStatus);
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  }, [q, cluster, status, family, contentStatus]);

  const queryString = useMemo(() => {
    const params = new URLSearchParams(filtersQueryString.startsWith("?") ? filtersQueryString.slice(1) : filtersQueryString);
    params.set("page", String(page));
    params.set("page_size", String(pageSize));
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  }, [filtersQueryString, page, pageSize]);

  const handleExport = async () => {
    setExporting(true);
    setError(null);
    try {
      const response = await authFetch(`/admin/professions/export${filtersQueryString}`, {
        method: "GET",
      });
      if (!response.ok) {
        throw new Error(`Экспорт не удался (${response.status})`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "professions_export.csv";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка экспорта CSV");
    } finally {
      setExporting(false);
    }
  };

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminFetch<ProfessionListApiResponse>(`/admin/professions${queryString}`);
      if (Array.isArray(data)) {
        setLegacyArrayMode(true);
        setRows(data);
        setTotal(data.length);
      } else {
        setLegacyArrayMode(false);
        setRows(Array.isArray(data.items) ? data.items : []);
        setTotal(typeof data.total === "number" ? data.total : 0);
      }
    } catch (err) {
      const e = err as Error & { status?: number };
      if (e.status === 404) {
        setError("API обновился, но контейнер web не перезагружен. Обновите страницу (Cmd+Shift+R).");
      } else {
        setError(err instanceof Error ? err.message : "Ошибка загрузки");
      }
    } finally {
      setLoading(false);
    }
  }, [queryString]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    setPage(1);
  }, [q, cluster, status, family, contentStatus]);

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  return (
    <section className="admin-page">
      <div className="admin-page-header-row">
        <h1>Profession Catalog</h1>
        <div style={{ display: "flex", gap: 8 }}>
          <button
            type="button"
            className="admin-btn admin-btn-ghost"
            onClick={() => void handleExport()}
            disabled={exporting}
          >
            {exporting ? "Экспорт..." : "Экспорт CSV"}
          </button>
          <Link href="/admin/professions/new" className="admin-btn admin-btn-primary">Новая профессия</Link>
        </div>
      </div>

      <div className="admin-filters">
        <input className="admin-input" placeholder="search slug/title" value={q} onChange={(e) => setQ(e.target.value)} />
        <select className="admin-input" value={cluster} onChange={(e) => setCluster(e.target.value)}>
          <option value="">Все группы (cluster)</option>
          {clusterOptions.map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
        <input className="admin-input" placeholder="status" value={status} onChange={(e) => setStatus(e.target.value)} />
        <input className="admin-input" placeholder="family" value={family} onChange={(e) => setFamily(e.target.value)} />
        <input className="admin-input" placeholder="content_status" value={contentStatus} onChange={(e) => setContentStatus(e.target.value)} />
        <button className="admin-btn admin-btn-primary" onClick={() => setPage(1)} type="button">Применить</button>
      </div>

      {!loading && !error && (
        <div className="admin-professions-stats-row">
          <span>Всего: {total}</span>
          <span>Активных: {activeCount}</span>
          <span>Деактивированных: {inactiveCount}</span>
          <label className="admin-professions-page-size-label">
            На странице:
            <select
              className="admin-input"
              value={String(pageSize)}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setPage(1);
              }}
            >
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="200">200</option>
            </select>
          </label>
          <span>Страница {page} из {totalPages}</span>
        </div>
      )}

      {loading && <div className="admin-loading">Загрузка...</div>}
      {error && <div className="admin-error">{error}</div>}

      {!loading && !error && (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Slug</th>
                <th>Title</th>
                <th>Cluster</th>
                <th>Status</th>
                <th>Completeness</th>
                <th>Действие</th>
              </tr>
            </thead>
            <tbody>
              {paginatedRows.map((row, index) => (
                <tr key={row.slug}>
                  <td>{(page - 1) * pageSize + index + 1}</td>
                  <td>{row.slug}</td>
                  <td>{row.title}</td>
                  <td>{row.cluster}</td>
                  <td><StatusBadge value={row.status} /></td>
                  <td>{row.completeness_score}%</td>
                  <td>
                    <Link href={`/admin/professions/${row.slug}`} className="admin-btn admin-btn-ghost">
                      Открыть
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="admin-pagination">
            <button
              type="button"
              className="admin-btn admin-btn-ghost admin-page-btn"
              disabled={page <= 1}
              onClick={() => setPage(1)}
            >
              « Первая
            </button>
            <button
              type="button"
              className="admin-btn admin-btn-ghost admin-page-btn"
              disabled={page <= 1}
              onClick={() => setPage((prev) => Math.max(1, prev - 1))}
            >
              ‹ Назад
            </button>
            {visiblePages.map((item, index) => {
              if (typeof item !== "number") {
                return (
                  <span key={`${item}-${index}`} className="admin-pagination-ellipsis" aria-hidden="true">
                    ...
                  </span>
                );
              }

              return (
                <button
                  key={item}
                  type="button"
                  className={`admin-btn ${item === page ? "admin-page-number-active" : "admin-btn-ghost admin-page-number"}`}
                  onClick={() => setPage(item)}
                >
                  {item}
                </button>
              );
            })}
            <button
              type="button"
              className="admin-btn admin-btn-ghost admin-page-btn"
              disabled={page >= totalPages}
              onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
            >
              Вперед ›
            </button>
            <button
              type="button"
              className="admin-btn admin-btn-ghost admin-page-btn"
              disabled={page >= totalPages}
              onClick={() => setPage(totalPages)}
            >
              Последняя »
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
