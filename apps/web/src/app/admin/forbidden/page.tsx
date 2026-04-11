"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type AdminMe = {
  email?: string;
  role?: string;
  is_active?: boolean;
};

type DebugState = {
  authEmail: string;
  hasAccessToken: boolean;
  hasRefreshToken: boolean;
  meStatus: number | null;
  meDetail: string;
};

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export default function AdminForbiddenPage() {
  const [me, setMe] = useState<AdminMe | null>(null);
  const [debug, setDebug] = useState<DebugState>({
    authEmail: "",
    hasAccessToken: false,
    hasRefreshToken: false,
    meStatus: null,
    meDetail: "",
  });

  useEffect(() => {
    const run = async () => {
      const token = localStorage.getItem("access_token");
      const refreshToken = localStorage.getItem("refresh_token");
      const authEmail = localStorage.getItem("auth_email") ?? "";

      setDebug((prev) => ({
        ...prev,
        authEmail,
        hasAccessToken: Boolean(token),
        hasRefreshToken: Boolean(refreshToken),
      }));

      if (!token) {
        setMe(null);
        setDebug((prev) => ({ ...prev, meStatus: 401, meDetail: "No access_token in localStorage" }));
        return;
      }
      try {
        const res = await fetch(`${apiBase}/admin/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          const detail = await res.text();
          setMe(null);
          setDebug((prev) => ({ ...prev, meStatus: res.status, meDetail: detail || "admin/me request failed" }));
          return;
        }

        const payload = (await res.json()) as AdminMe;
        setMe(payload);
        setDebug((prev) => ({ ...prev, meStatus: 200, meDetail: "OK" }));
      } catch (err) {
        setMe(null);
        setDebug((prev) => ({
          ...prev,
          meStatus: 0,
          meDetail: err instanceof Error ? err.message : "Network error",
        }));
      }
    };
    void run();
  }, []);

  return (
    <main className="admin-forbidden">
      <h1>403 — Доступ запрещен</h1>
      <p>У вас нет прав для входа в административный раздел.</p>
      {me && (
        <p className="admin-help">
          Текущий аккаунт: {me.email ?? "unknown"}, роль: {me.role ?? "unknown"}, active: {String(me.is_active)}
        </p>
      )}
      <div className="admin-editor-box" style={{ marginTop: "0.75rem" }}>
        <div className="admin-editor-box-title">Диагностика доступа</div>
        <p className="admin-help">auth_email: {debug.authEmail || "(empty)"}</p>
        <p className="admin-help">has access_token: {String(debug.hasAccessToken)}</p>
        <p className="admin-help">has refresh_token: {String(debug.hasRefreshToken)}</p>
        <p className="admin-help">/admin/me status: {debug.meStatus ?? "(none)"}</p>
        <p className="admin-help">/admin/me detail: {debug.meDetail || "(none)"}</p>
      </div>
      <div className="admin-form-actions">
        <button
          type="button"
          className="admin-btn admin-btn-ghost"
          onClick={() => {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            localStorage.removeItem("auth_email");
            window.location.href = "/login";
          }}
        >
          Сбросить сессию
        </button>
        <Link href="/dashboard" className="admin-btn admin-btn-primary">
          Вернуться в кабинет
        </Link>
      </div>
    </main>
  );
}
