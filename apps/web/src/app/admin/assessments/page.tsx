"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { StatusBadge } from "@/components/admin/status-badge";
import { adminFetch } from "@/lib/admin-api";

type AssessmentRow = {
  id: string;
  slug: string;
  title: string;
  target_items_count: number;
  expected_duration_min: number;
  is_active: boolean;
  version: number;
};

export default function AssessmentsListPage() {
  const [rows, setRows] = useState<AssessmentRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await adminFetch<AssessmentRow[]>("/admin/assessments");
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
    void run();
  }, []);

  return (
    <section className="admin-page">
      <h1>Assessments</h1>
      {loading && <div className="admin-loading">Загрузка...</div>}
      {error && <div className="admin-error">{error}</div>}
      {!loading && !error && (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Slug</th>
                <th>Title</th>
                <th>Items</th>
                <th>Duration</th>
                <th>Status</th>
                <th>Version</th>
                <th>Действие</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td>{row.slug}</td>
                  <td>{row.title}</td>
                  <td>{row.target_items_count}</td>
                  <td>{row.expected_duration_min} мин</td>
                  <td><StatusBadge value={row.is_active ? "active" : "draft"} /></td>
                  <td>{row.version}</td>
                  <td>
                    <Link href={`/admin/assessments/${row.slug}`} className="admin-btn admin-btn-ghost">
                      Открыть
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
