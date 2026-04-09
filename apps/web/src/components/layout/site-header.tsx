import Link from "next/link";

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
          <Link href="/login" className="header-btn header-btn-ghost">
            Войти
          </Link>
          <Link href="/register" className="header-btn header-btn-primary">
            Пройти тест
          </Link>
        </div>
      </div>
    </header>
  );
}