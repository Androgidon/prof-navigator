"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { StatusBadge } from "@/components/admin/status-badge";
import { adminFetch } from "@/lib/admin-api";

type ProfessionRow = {
  slug: string;
  title: string;
  cluster: string;
  status: string;
  completeness_score: number;
};

export default function ProfessionsListPage() {
  const [rows, setRows] = useState<ProfessionRow[]>([]);
  const [q, setQ] = useState("");
  const [cluster, setCluster] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const queryString = useMemo(() => {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (cluster) params.set("cluster", cluster);
    if (status) params.set("status", status);
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  }, [q, cluster, status]);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminFetch<ProfessionRow[]>(`/admin/professions${queryString}`);
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
        <h1>Profession Catalog</h1>
        <Link href="/admin/professions/new" className="admin-btn admin-btn-primary">Новая профессия</Link>
      </div>

      <div className="admin-filters">
        <input className="admin-input" placeholder="search slug/title" value={q} onChange={(e) => setQ(e.target.value)} />
        <input className="admin-input" placeholder="cluster" value={cluster} onChange={(e) => setCluster(e.target.value)} />
        <input className="admin-input" placeholder="status" value={status} onChange={(e) => setStatus(e.target.value)} />
        <button className="admin-btn admin-btn-primary" onClick={() => void load()} type="button">Применить</button>
      </div>

      {loading && <div className="admin-loading">Загрузка...</div>}
      {error && <div className="admin-error">{error}</div>}

      {!loading && !error && (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Slug</th>
                <th>Title</th>
                <th>Cluster</th>
                <th>Status</th>
                <th>Completeness</th>
                <th>Действие</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.slug}>
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
        </div>
      )}
    </section>
  );
}
