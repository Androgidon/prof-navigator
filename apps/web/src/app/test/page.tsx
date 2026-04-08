"use client";

import { useCallback, useState } from "react";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export default function TestPage() {
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startTest = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiUrl}/assessments/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "anon", assessment_id: "0001" }),
      });
      if (!res.ok) {
        throw new Error("Не удалось создать сессию");
      }
      const payload = await res.json();
      setSessionId(payload.session_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка");
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <section className="mx-auto flex w-full max-w-4xl flex-col gap-8 px-6 py-16">
      <header className="space-y-3">
        <p className="text-xs uppercase tracking-[0.4em] text-slate-400">Тест</p>
        <h1 className="text-3xl font-semibold text-white">30+ вопросов, чтобы понять себя</h1>
        <p className="text-sm text-slate-300">
          Блоковый формат, сохранение прогресса и адаптивный интерфейс создают спокойную атмосферу для
          прохождения теста.
        </p>
      </header>
      <div className="space-y-6 rounded-3xl border border-white/10 bg-slate-900/60 p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-white">Начать новый тест</h2>
          <button
            onClick={startTest}
            className="rounded-full border border-amber-400/60 bg-amber-400/20 px-5 py-2 text-xs font-semibold uppercase tracking-[0.4em] text-amber-200 transition hover:border-amber-300"
            disabled={loading}
          >
            {loading ? "Загрузка" : "Создать сессию"}
          </button>
        </div>
        {sessionId && (
          <p className="text-sm text-emerald-400">Сессия создана: {sessionId}</p>
        )}
        {error && <p className="text-sm text-rose-400">{error}</p>}
        <div className="text-sm text-slate-300">
          После старта мы будем загружать блоки вопросов, сохранять ответы и автоматически обновлять
          прогресс. Фейковые данные в этом прототипе создаются через API.
        </div>
      </div>
      <section className="grid gap-6 md:grid-cols-2">
        {["Когнитивные", "Коммуникационные", "Технические", "Креатив"]
          .map((tag) => (
            <article key={tag} className="rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900/70 to-slate-900/30 p-6">
              <p className="text-xs uppercase tracking-[0.4em] text-slate-400">Блок</p>
              <h3 className="text-lg font-semibold text-white">{tag}</h3>
              <p className="mt-3 text-sm text-slate-300">
                Использует адаптивную логику: если текущие ответы говорят о склонности к {tag.toLowerCase()} —
                добавляем дополнительные вопросы в тот же блок.
              </p>
            </article>
          ))}
      </section>
    </section>
  );
}
