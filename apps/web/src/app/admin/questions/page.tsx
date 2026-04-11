"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { QuestionFiltersBar } from "@/components/admin/question-filters-bar";
import { StatusBadge } from "@/components/admin/status-badge";
import { adminFetch } from "@/lib/admin-api";

type QuestionRow = {
  id: string;
  assessment_version_slug: string;
  question_id: string;
  block: string;
  question_type: string;
  primary_dimension: string;
  order_hint: number;
  status: string;
};

type Filters = {
  assessment_slug: string;
  block: string;
  question_type: string;
  status_filter: string;
  q: string;
};

const defaultFilters: Filters = {
  assessment_slug: "",
  block: "",
  question_type: "",
  status_filter: "",
  q: "",
};

export default function QuestionListPage() {
  const [rows, setRows] = useState<QuestionRow[]>([]);
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const queryString = useMemo(() => {
    const params = new URLSearchParams();
    if (filters.assessment_slug) params.set("assessment_slug", filters.assessment_slug);
    if (filters.block) params.set("block", filters.block);
    if (filters.question_type) params.set("question_type", filters.question_type);
    if (filters.status_filter) params.set("status_filter", filters.status_filter);
    if (filters.q) params.set("q", filters.q);
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  }, [filters]);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminFetch<QuestionRow[]>(`/admin/questions${queryString}`);
      setRows(data);
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
  };

  useEffect(() => {
    void load();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="admin-page">
      <div className="admin-page-header-row">
        <h1>Question Bank</h1>
        <Link className="admin-btn admin-btn-primary" href="/admin/questions/new">Новый вопрос</Link>
      </div>

      <QuestionFiltersBar value={filters} onChange={setFilters} onApply={() => void load()} />

      {loading && <div className="admin-loading">Загрузка...</div>}
      {error && <div className="admin-error">{error}</div>}

      {!loading && !error && (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Assessment</th>
                <th>Question ID</th>
                <th>Block</th>
                <th>Type</th>
                <th>Primary</th>
                <th>Order</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td>{row.assessment_version_slug}</td>
                  <td>
                    <Link href={`/admin/questions/${row.assessment_version_slug}/${row.question_id}`}>
                      {row.question_id}
                    </Link>
                  </td>
                  <td>{row.block}</td>
                  <td>{row.question_type}</td>
                  <td>{row.primary_dimension}</td>
                  <td>{row.order_hint}</td>
                  <td><StatusBadge value={row.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
