"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { adminFetch } from "@/lib/admin-api";

type MatrixRow = {
  profession_slug: string;
  profession_title: string;
  cluster: string;
  version_slug: string;
  completeness_score: number;
  validation_status: string;
};

export default function MatrixListPage() {
  const [rows, setRows] = useState<MatrixRow[]>([]);
  const [versionSlug, setVersionSlug] = useState("");
  const [professionQ, setProfessionQ] = useState("");
  const [cluster, setCluster] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const queryString = useMemo(() => {
    const params = new URLSearchParams();
    if (versionSlug) params.set("version_slug", versionSlug);
    if (professionQ) params.set("profession_q", professionQ);
    if (cluster) params.set("cluster", cluster);
    const qs = params.toString();
    return qs ? `?${qs}` : "";
  }, [versionSlug, professionQ, cluster]);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await adminFetch<MatrixRow[]>(`/admin/matrix${queryString}`);
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
      <h1>Matrix List</h1>

      <div className="admin-filters">
        <input className="admin-input" placeholder="version_slug" value={versionSlug} onChange={(e) => setVersionSlug(e.target.value)} />
        <input className="admin-input" placeholder="profession search" value={professionQ} onChange={(e) => setProfessionQ(e.target.value)} />
        <input className="admin-input" placeholder="cluster" value={cluster} onChange={(e) => setCluster(e.target.value)} />
        <button className="admin-btn admin-btn-primary" type="button" onClick={() => void load()}>
          Применить
        </button>
      </div>

      {loading && <div className="admin-loading">Загрузка...</div>}
      {error && <div className="admin-error">{error}</div>}

      {!loading && !error && (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Profession</th>
                <th>Cluster</th>
                <th>Version</th>
                <th>Completeness</th>
                <th>Validation</th>
                <th>Действие</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={`${row.version_slug}-${row.profession_slug}`}>
                  <td>{row.profession_title}</td>
                  <td>{row.cluster}</td>
                  <td>{row.version_slug}</td>
                  <td>{row.completeness_score}%</td>
                  <td>{row.validation_status}</td>
                  <td>
                    <Link href={`/admin/matrix/${row.version_slug}/${row.profession_slug}`} className="admin-btn admin-btn-ghost">
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
