import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CareerPath — explainable профессиональный навигатор",
  description:
    "CareerPath помогает школьникам и абитуриентам пройти тест, получить рекомендованные профессии и практичные next step.",
};

const navItems = [
  { label: "Главный", href: "/" },
  { label: "Регистрация", href: "/register" },
  { label: "Тест", href: "/test" },
  { label: "Результаты", href: "/results" },
  { label: "Dashboard", href: "/dashboard" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" className={`${geistSans.variable} ${geistMono.variable} scroll-smooth`}>
      <body className="min-h-screen bg-slate-950 text-white">
        <header className="border-b border-white/10 bg-slate-950/80 backdrop-blur">
          <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
            <div className="text-sm tracking-[0.4em] text-amber-400">CareerPath</div>
            <nav className="flex gap-4 text-xs uppercase tracking-[0.3em] text-slate-300">
              {navItems.map((item) => (
                <Link key={item.href} href={item.href} className="hover:text-white">
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col">
          {children}
        </main>
      </body>
    </html>
  );
}
