import Link from "next/link";

interface FooterColumn {
  title: string;
  links: { label: string; href: string }[];
}

const footerColumns: FooterColumn[] = [
  {
    title: "Продукт",
    links: [
      { label: "Тест", href: "/test" },
      { label: "Профессии", href: "/professions" },
      { label: "Как это работает", href: "/#how-it-works" },
    ],
  },
  {
    title: "Компания",
    links: [
      { label: "О нас", href: "/about" },
      { label: "Контакты", href: "/contacts" },
      { label: "Политика конфиденциальности", href: "/privacy" },
    ],
  },
  {
    title: "Поддержка",
    links: [
      { label: "FAQ", href: "/faq" },
      { label: "Помощь", href: "/help" },
    ],
  },
];

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="footer-container">
        <div className="footer-brand">
          <p className="footer-logo">CareerPath</p>
          <p className="footer-tagline">Помогаем школьникам найти свой путь в будущее</p>
        </div>
        <div className="footer-nav">
          {footerColumns.map((column) => (
            <div key={column.title} className="footer-column">
              <p className="footer-column-title">{column.title}</p>
              {column.links.map((link) => (
                <Link key={link.href} href={link.href} className="footer-link">
                  {link.label}
                </Link>
              ))}
            </div>
          ))}
        </div>
      </div>
      <div className="footer-bottom">
        <p className="footer-copyright">© 2026 CareerPath. Все права защищены.</p>
      </div>
    </footer>
  );
}