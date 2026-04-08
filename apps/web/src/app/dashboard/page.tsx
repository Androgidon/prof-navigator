"use client";

import Link from "next/link";

export default function DashboardPage() {
  const cards = [
    { label: "Мой профиль", href: "/register", description: "Заполните профиль, чтобы улучшить рекомендации" },
    { label: "Тест", href: "/test", description: "Пробегитесь по блокам и сохраняйте прогресс" },
    { label: "Результаты", href: "/results", description: "Узнайте рекомендуемые профессии" },
  ];

  return (
    <section className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-6 py-16">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Dashboard</p>
        <h1 className="text-3xl font-semibold text-white">Личный кабинет</h1>
        <p className="text-sm text-slate-300">Следите за прохождением теста, сохраненными профессиями и рекомендациями.</p>
      </header>
      <div className="grid gap-6 md:grid-cols-3">
        {cards.map((card) => (
          <Link
            key={card.label}
            href={card.href}
            className="flex flex-col gap-3 rounded-3xl border border-white/10 bg-slate-900/60 p-5 text-sm text-slate-300 transition hover:border-amber-400"
          >
            <h2 className="text-lg font-semibold text-white">{card.label}</h2>
            <p>{card.description}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
