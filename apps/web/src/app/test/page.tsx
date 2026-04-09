"use client";

import { useCallback, useState } from "react";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { FocusedTaskLayout } from "@/components/layout/focused-task-layout";
import { ProgressBar } from "@/components/layout/progress-bar";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

const testBlocks = [
  {
    label: "Блок",
    title: "Когнитивные",
    description: "Анализ мышления, логики и способности решать задачи.",
  },
  {
    label: "Блок",
    title: "Коммуникационные",
    description: "Оценка навыков общения и работы с людьми.",
  },
  {
    label: "Блок",
    title: "Технические",
    description: "Понимание технологий и технического мышления.",
  },
  {
    label: "Блок",
    title: "Креативные",
    description: "Творческие способности и нестандартное мышление.",
  },
];

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
    <div className="min-h-screen bg-background">
      <SiteHeader />

      <FocusedTaskLayout>
        <ProgressBar value={0} max={100} />

        <div className="test-start-surface">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">
            Тест
          </p>
          <h1>30+ вопросов, чтобы понять себя</h1>
          <p>
            Блоковый формат, сохранение прогресса и адаптивный интерфейс создают спокойную атмосферу для
            прохождения теста.
          </p>

          <div className="test-start-header">
            <h2>Начать новый тест</h2>
            <button
              onClick={startTest}
              className="test-start-btn"
              disabled={loading}
            >
              {loading ? "Загрузка..." : "Создать сессию"}
            </button>
          </div>

          {sessionId && (
            <p className="text-sm text-success mt-4">
              Сессия создана: {sessionId}
            </p>
          )}
          {error && (
            <p className="text-sm text-destructive mt-4">{error}</p>
          )}
        </div>

        <div className="test-blocks-grid">
          {testBlocks.map((block) => (
            <article key={block.title} className="test-block-card">
              <p>{block.label}</p>
              <h3>{block.title}</h3>
              <p>{block.description}</p>
            </article>
          ))}
        </div>
      </FocusedTaskLayout>

      <SiteFooter />
    </div>
  );
}