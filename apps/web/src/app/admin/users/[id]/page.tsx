"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

type UserDetailPayload = {
  account: {
    id: string;
    email: string;
    role: string;
    is_active: boolean;
    created_at: string | null;
  };
  profile: {
    full_name: string | null;
    birth_date: string | null;
    country: string | null;
    region: string | null;
    city: string | null;
    language: string | null;
    grades: Record<string, number> | null;
    interests: string[] | null;
    created_at: string | null;
  } | null;
  recommendations: Array<{
    id: string;
    score: number;
    rank: number;
    profession_id: string;
    profession_title: string | null;
    created_at: string | null;
  }>;
  favorites: Array<{
    id: string;
    profession_id: string;
    profession_title: string | null;
    note: string | null;
    created_at: string | null;
  }>;
};

export default function AdminUserDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const userId = params.id;
  const [data, setData] = useState<UserDetailPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        router.replace("/dashboard");
        return;
      }

      const res = await fetch(`${apiBase}/admin/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.status === 401 || res.status === 403) {
        router.replace("/dashboard");
        return;
      }
      if (!res.ok) {
        throw new Error("Не удалось загрузить пользователя");
      }
      setData(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка");
    } finally {
      setLoading(false);
    }
  }, [router, userId]);

  useEffect(() => {
    void load();
  }, [load]);

  const changeStatus = async (action: "activate" | "deactivate" | "delete") => {
    const isDelete = action === "delete";
    if (isDelete && !window.confirm("Подтвердите soft-delete пользователя")) {
      return;
    }

    const method = action === "delete" ? "DELETE" : "POST";
    const path = action === "delete" ? `${apiBase}/admin/users/${userId}` : `${apiBase}/admin/users/${userId}/${action}`;

    const token = localStorage.getItem("access_token");
    if (!token) {
      router.replace("/dashboard");
      return;
    }

    const res = await fetch(path, {
      method,
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.status === 401 || res.status === 403) {
      router.replace("/dashboard");
      return;
    }
    if (!res.ok) {
      alert("Не удалось выполнить действие");
      return;
    }
    await load();
  };

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />
      <main className="dashboard-content">
        <div className="dashboard-header">
          <h1 className="dashboard-title">Пользователь</h1>
          <Link href="/admin/users" className="header-btn header-btn-ghost">Назад к списку</Link>
        </div>

        {loading && <div className="loading-state">Загрузка...</div>}
        {error && <div className="error-state">{error}</div>}

        {data && (
          <div className="space-y-4">
            <div className="settings-card">
              <h2 className="dashboard-section-heading">Account</h2>
              <p><strong>ID:</strong> {data.account.id}</p>
              <p><strong>Email:</strong> {data.account.email}</p>
              <p><strong>Role:</strong> {data.account.role}</p>
              <p><strong>Status:</strong> {data.account.is_active ? "active" : "deactivated"}</p>
              <p><strong>Created at:</strong> {data.account.created_at ? new Date(data.account.created_at).toLocaleString() : "—"}</p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
                <button className="form-submit-btn mt-0" type="button" onClick={() => changeStatus("deactivate")}>Deactivate</button>
                <button className="form-submit-btn mt-0" type="button" onClick={() => changeStatus("activate")}>Activate</button>
                <button className="form-submit-btn mt-0" type="button" onClick={() => changeStatus("delete")}>Delete</button>
              </div>
            </div>

            <div className="settings-card">
              <h2 className="dashboard-section-heading">UserProfile</h2>
              {data.profile ? (
                <div className="space-y-1">
                  <p><strong>full_name:</strong> {data.profile.full_name ?? "—"}</p>
                  <p><strong>birth_date:</strong> {data.profile.birth_date ?? "—"}</p>
                  <p><strong>country:</strong> {data.profile.country ?? "—"}</p>
                  <p><strong>region:</strong> {data.profile.region ?? "—"}</p>
                  <p><strong>city:</strong> {data.profile.city ?? "—"}</p>
                  <p><strong>language:</strong> {data.profile.language ?? "—"}</p>
                  <p><strong>grades:</strong> {data.profile.grades ? JSON.stringify(data.profile.grades) : "—"}</p>
                  <p><strong>interests:</strong> {data.profile.interests ? data.profile.interests.join(", ") : "—"}</p>
                </div>
              ) : (
                <p className="settings-placeholder">Профиль отсутствует</p>
              )}
            </div>

            <div className="settings-card">
              <h2 className="dashboard-section-heading">Recommendations</h2>
              {data.recommendations.length > 0 ? (
                <ul className="space-y-2">
                  {data.recommendations.map((rec) => (
                    <li key={rec.id}>
                      #{rec.rank} {rec.profession_title ?? rec.profession_id} (score: {rec.score})
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="settings-placeholder">Нет рекомендаций</p>
              )}
            </div>

            <div className="settings-card">
              <h2 className="dashboard-section-heading">Favorites</h2>
              {data.favorites.length > 0 ? (
                <ul className="space-y-2">
                  {data.favorites.map((fav) => (
                    <li key={fav.id}>{fav.profession_title ?? fav.profession_id}</li>
                  ))}
                </ul>
              ) : (
                <p className="settings-placeholder">Нет избранного</p>
              )}
            </div>
          </div>
        )}
      </main>
      <SiteFooter />
    </div>
  );
}
