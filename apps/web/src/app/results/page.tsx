"use client";

import { useEffect, useState } from "react";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

type Recommendation = {
  profession: string;
  slug: string;
  score: number;
  rank: number;
  explanation: string[];
};

export default function ResultsPage() {
  const [results, setResults] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    const fetchRecommendations = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${apiUrl}/recommendations`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          signal: controller.signal,
          body: JSON.stringify({
            user_id: "anon",
            vector: { analytical: 0.8, creative: 0.4, social: 0.6 },
            interests: ["it", "design"],
          }),
        });
        if (!response.ok) {
          throw new Error("Не удалось получить рекомендации");
        }
        const payload = await response.json();
        setResults(payload.recommendations ?? []);
      } catch (err) {
        if ((err as Error).name === "AbortError") {
          return;
        }
        setError(err instanceof Error ? err.message : "Ошибка при загрузке");
      } finally {
        setLoading(false);
      }
    };

    void fetchRecommendations();

    return () => controller.abort();
  }, []);

  return (
    <section className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-6 py-16">
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Результаты</p>
        <h1 className="text-3xl font-semibold text-white">Персональные рекомендации</h1>
        <p className="text-sm text-slate-300">
          Сформированы на основе официального вектора и сохранённых предпочтений. Каждый результат содержит
          объяснение и конкретные шаги.
        </p>
      </header>
      {loading && <p className="text-sm text-amber-300">Загружаем рекомендации...</p>}
      {error && <p className="text-sm text-rose-400">{error}</p>}
      <div className="grid gap-6 md:grid-cols-2">
        {results.map((item) => (
          <article
            key={item.slug}
            className="flex flex-col gap-3 rounded-3xl border border-white/10 bg-slate-900/60 p-6"
          >
            <div className="flex items-baseline justify-between">
              <h2 className="text-xl font-semibold text-white">{item.slug}</h2>
              <span className="text-xs uppercase tracking-[0.4em] text-slate-400">#{item.rank}</span>
            </div>
            <p className="text-sm text-slate-300">Score: {item.score}</p>
            <ul className="text-sm text-slate-200">
              {item.explanation.map((note) => (
                <li key={note}>• {note}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}
