"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { clearAuthStorage, getTestEntryRoute } from "@/lib/auth-flow";

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

interface NavItem {
  label: string;
  href: string;
}

const navItems: NavItem[] = [
  { label: "Профессии", href: "/professions" },
  { label: "Как это работает", href: "/#how-it-works" },
  { label: "О проекте", href: "/about" },
];

export function SiteHeader() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    if (typeof window === "undefined") {
      return false;
    }
    return Boolean(localStorage.getItem("access_token"));
  });
  const [testEntryHref, setTestEntryHref] = useState<"/login" | "/onboarding" | "/test">(() => {
    if (typeof window === "undefined") {
      return "/login";
    }
    return getTestEntryRoute();
  });
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const checkAdmin = async () => {
      if (typeof window === "undefined") {
        return;
      }
      const token = localStorage.getItem("access_token");
      if (!token) {
        setIsAdmin(false);
        return;
      }

      try {
        const res = await fetch(`${apiBase}/admin/users`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setIsAdmin(res.ok);
      } catch {
        setIsAdmin(false);
      }
    };

    void checkAdmin();
  }, [isAuthenticated]);

  const handleLogout = () => {
    clearAuthStorage();
    setIsAuthenticated(false);
    setTestEntryHref("/login");
    router.push("/login");
  };

  return (
    <header className="site-header">
      <div className="header-container">
        <div className="header-brand">
          <Link href="/" className="brand-link">
            <p className="brand-logo">CareerPath</p>
            <p className="brand-tagline">Профориентация для школьников</p>
          </Link>
        </div>
        <nav className="header-nav" aria-label="Основная навигация">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="header-nav-link">
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="header-actions">
          {isAuthenticated ? (
            <>
              <Link href="/dashboard" className="header-btn header-btn-ghost" aria-label="Личный кабинет" title="Личный кабинет">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M20 21a8 8 0 1 0-16 0" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </Link>
              {isAdmin && (
                <Link href="/admin/users" className="header-btn header-btn-ghost">
                  Админка
                </Link>
              )}
              <button type="button" className="header-btn header-btn-ghost" onClick={handleLogout}>
                Выйти
              </button>
            </>
          ) : (
            <Link href="/login" className="header-btn header-btn-ghost">
              Войти
            </Link>
          )}
          <Link href={testEntryHref} className="header-btn header-btn-primary">
            Пройти тест
          </Link>
        </div>
      </div>
    </header>
  );
}