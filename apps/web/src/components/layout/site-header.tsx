"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { clearAuthStorage, getTestEntryRoute } from "@/lib/auth-flow";

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
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [testEntryHref, setTestEntryHref] = useState<"/login" | "/onboarding" | "/test">("/login");

  useEffect(() => {
    const syncAuthState = () => {
      setIsAuthenticated(Boolean(localStorage.getItem("access_token")));
      setTestEntryHref(getTestEntryRoute());
    };

    const frame = window.requestAnimationFrame(syncAuthState);
    window.addEventListener("careerpath:auth-changed", syncAuthState);

    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener("careerpath:auth-changed", syncAuthState);
    };
  }, []);

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
              <Link href="/dashboard" className="header-btn header-btn-ghost" aria-label="Персональный кабинет" title="Персональный кабинет">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M20 21a8 8 0 1 0-16 0" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                <span>Профиль</span>
              </Link>
              <Link href="/admin" className="header-btn header-btn-ghost">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M12 2l3 6 6 .9-4.5 4.3 1.1 6.3L12 16.8 6.4 19.5l1.1-6.3L3 8.9 9 8z" />
                </svg>
                <span>Админка</span>
              </Link>
              <button type="button" className="header-btn header-btn-ghost" onClick={handleLogout}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                  <polyline points="16 17 21 12 16 7" />
                  <line x1="21" y1="12" x2="9" y2="12" />
                </svg>
                <span>Выйти</span>
              </button>
            </>
          ) : (
            <Link href="/login" className="header-btn header-btn-ghost">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                <polyline points="10 17 15 12 10 7" />
                <line x1="15" y1="12" x2="3" y2="12" />
              </svg>
              <span>Войти</span>
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