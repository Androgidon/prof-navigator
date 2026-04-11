"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { authFetch, AuthExpiredError } from "@/lib/api-client";

type AdminUser = {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string | null;
};

export default function AdminUsersPage() {
  const router = useRouter();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadUsers = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await authFetch("/admin/users");
        if (res.status === 403) {
          router.replace("/dashboard");
          return;
        }
        if (!res.ok) {
          throw new Error("Не удалось загрузить пользователей");
        }
        const payload = await res.json();
        setUsers(payload.users ?? []);
      } catch (err) {
        if (err instanceof AuthExpiredError) {
          return;
        }
        setError(err instanceof Error ? err.message : "Ошибка");
      } finally {
        setLoading(false);
      }
    };

    void loadUsers();
  }, [router]);

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />
      <main className="dashboard-content">
        <div className="dashboard-header">
          <h1 className="dashboard-title">Админка: пользователи</h1>
        </div>

        {loading && <div className="loading-state">Загрузка...</div>}
        {error && <div className="error-state">{error}</div>}

        {!loading && !error && (
          <div className="settings-card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b border-border">
                  <th className="py-2 pr-4">ID</th>
                  <th className="py-2 pr-4">Email</th>
                  <th className="py-2 pr-4">Role</th>
                  <th className="py-2 pr-4">Status</th>
                  <th className="py-2 pr-4">Created at</th>
                  <th className="py-2 pr-4">Действие</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b border-border/50">
                    <td className="py-2 pr-4 font-mono text-xs">{user.id}</td>
                    <td className="py-2 pr-4">{user.email}</td>
                    <td className="py-2 pr-4">{user.role}</td>
                    <td className="py-2 pr-4">{user.is_active ? "active" : "deactivated"}</td>
                    <td className="py-2 pr-4">{user.created_at ? new Date(user.created_at).toLocaleString() : "—"}</td>
                    <td className="py-2 pr-4">
                      <Link href={`/admin/users/${user.id}`} className="header-btn header-btn-ghost">
                        Подробнее
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
      <SiteFooter />
    </div>
  );
}
