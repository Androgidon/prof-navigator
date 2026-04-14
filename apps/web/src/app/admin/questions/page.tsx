"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { QuestionFiltersBar } from "@/components/admin/question-filters-bar";
import { StatusBadge } from "@/components/admin/status-badge";
import { adminFetch } from "@/lib/admin-api";
import { authFetch } from "@/lib/api-client";

type QuestionRow = {
  id: string;
  assessment_version_slug: string;
  question_id: string;
  block: string;
  subblock?: string | null;
  question_type: string;
  text: string;
  primary_dimension: string;
  order_hint: number;
  question_purpose?: string;
  active_in_scoring: boolean;
  experiment_tag?: string | null;
  experiment_mode?: string | null;
  status: string;
  updated_at?: string | null;
};

type QuestionSummary = {
  total_questions: number;
  active_baseline: number;
  active_experimental: number;
  inactive_or_draft: number;
};

type QuestionListPageResponse = {
  items: QuestionRow[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

type QuestionListApiResponse = QuestionListPageResponse | QuestionRow[];

type Filters = {
  assessment_slug: string;
  block: string;
  question_type: string;
  status_filter: string;
  question_purpose: string;
  experiment_mode: string;
  experiment_tag: string;
  q: string;
};

const defaultFilters: Filters = {
  assessment_slug: "",
  block: "",
  question_type: "",
  status_filter: "",
  question_purpose: "",
  experiment_mode: "",
  experiment_tag: "",
  q: "",
};

export default function QuestionListPage() {
  const [rows, setRows] = useState<QuestionRow[]>([]);
  const [summary, setSummary] = useState<QuestionSummary | null>(null);
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [pageSize, setPageSize] = useState(20);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [legacyArrayMode, setLegacyArrayMode] = useState(false);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const filtersQueryString = useMemo(() => {
    const params = new URLSearchParams();
    if (filters.assessment_slug) params.set("assessment_slug", filters.assessment_slug);
    if (filters.block) params.set("block", filters.block);
    if (filters.question_type) params.set("question_type", filters.question_type);
    if (filters.status_filter) params.set("status_filter", filters.status_filter);
    if (filters.question_purpose) params.set("question_purpose", filters.question_purpose);
    if (filters.experiment_mode) params.set("experiment_mode", filters.experiment_mode);
    if (filters.experiment_tag) params.set("experiment_tag", filters.experiment_tag);
    if (filters.q) params.set("q", filters.q);
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  }, [filters]);

  const queryString = useMemo(() => {
    const params = new URLSearchParams(filtersQueryString.startsWith("?") ? filtersQueryString.slice(1) : filtersQueryString);
    params.set("page", String(page));
    params.set("page_size", String(pageSize));
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  }, [filtersQueryString, page, pageSize]);

  const handleExport = useCallback(async () => {
    setExporting(true);
    setError(null);
    try {
      const response = await authFetch(`/admin/questions/export${filtersQueryString}`, {
        method: "GET",
      });
      if (!response.ok) {
        throw new Error(`Экспорт не удался (${response.status})`);
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "questions_export.csv";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка экспорта CSV");
    } finally {
      setExporting(false);
    }
  }, [filtersQueryString]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const summaryParams = new URLSearchParams();
      if (filters.assessment_slug) summaryParams.set("assessment_slug", filters.assessment_slug);
      const summaryQuery = summaryParams.toString();
      const [data, summaryData] = await Promise.all([
        adminFetch<QuestionListApiResponse>(`/admin/questions${queryString}`),
        adminFetch<QuestionSummary>(`/admin/questions/summary${summaryQuery ? `?${summaryQuery}` : ""}`),
      ]);

      if (Array.isArray(data)) {
        setLegacyArrayMode(true);
        setRows(data);
        setTotal(data.length);
      } else {
        setLegacyArrayMode(false);
        setRows(data.items ?? []);
        setTotal(data.total ?? 0);
      }
      setSummary(summaryData);
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
  }, [filters.assessment_slug, queryString]);

  useEffect(() => {
    void load();
  }, [load]);

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / pageSize)), [total, pageSize]);
  const displayRows = useMemo(() => {
    if (!legacyArrayMode) return rows;
    const start = (page - 1) * pageSize;
    return rows.slice(start, start + pageSize);
  }, [legacyArrayMode, rows, page, pageSize]);
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

  return (
    <section className="admin-page">
      <div className="admin-page-header-row">
        <h1>Question Bank</h1>
        <div style={{ display: "flex", gap: 8 }}>
          <button
            type="button"
            className="admin-btn admin-btn-ghost"
            onClick={() => void handleExport()}
            disabled={exporting}
          >
            {exporting ? "Экспорт..." : "Экспорт CSV"}
          </button>
          <Link className="admin-btn admin-btn-primary" href="/admin/questions/new">Новый вопрос</Link>
        </div>
      </div>

      <QuestionFiltersBar value={filters} onChange={setFilters} onApply={() => setPage(1)} />

      {summary && (
        <div className="admin-professions-stats-row">
          <span>Всего вопросов: {summary.total_questions}</span>
          <span>Активных baseline: {summary.active_baseline}</span>
          <span>Активных experimental: {summary.active_experimental}</span>
          <span>Inactive / draft: {summary.inactive_or_draft}</span>
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
                <th>Question ID</th>
                <th>Assessment</th>
                <th>Text</th>
                <th>Type</th>
                <th>Block</th>
                <th>Purpose</th>
                <th>Status</th>
                <th>Active in scoring</th>
                <th>Experiment</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              {displayRows.map((row, index) => (
                <tr key={row.id}>
                  <td>
                    {(page - 1) * pageSize + index + 1}. <Link href={`/admin/questions/${row.assessment_version_slug}/${row.question_id}`}>
                      {row.question_id}
                    </Link>
                  </td>
                  <td>{row.assessment_version_slug}</td>
                  <td>{row.text}</td>
                  <td>{row.question_type}</td>
                  <td>{row.block}{row.subblock ? ` / ${row.subblock}` : ""}</td>
                  <td>{row.question_purpose ?? "-"}</td>
                  <td><StatusBadge value={row.status} /></td>
                  <td>{row.active_in_scoring ? "yes" : "no"}</td>
                  <td>{row.experiment_mode ?? row.experiment_tag ?? "baseline"}</td>
                  <td>{row.updated_at ? new Date(row.updated_at).toLocaleString("ru-RU") : "-"}</td>
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
