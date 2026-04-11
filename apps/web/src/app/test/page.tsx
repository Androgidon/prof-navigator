"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { FocusedTaskLayout } from "@/components/layout/focused-task-layout";
import { ProgressBar } from "@/components/layout/progress-bar";
import { AssessmentHeader } from "@/components/layout/assessment-header";
import { QuestionCard } from "@/components/layout/question-card";
import { AnswerOptionRow } from "@/components/layout/answer-option-row";
import { getTestEntryRoute } from "@/lib/auth-flow";
import { authFetch, AuthExpiredError } from "@/lib/api-client";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

function getAuthHeaders(includeJson = false): Record<string, string> {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  return {
    ...(includeJson ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

interface QuestionItem {
  question_id: string;
  block: string;
  question_type: string;
  text: string;
  options: Array<{ key?: string; value?: number; label: string }>;
  is_required: boolean;
}

const blockLabels: Record<string, string> = {
  interests_and_task_preferences: "Интересы и задачи",
  subjects_profile: "Предметный профиль",
  hobbies_and_activities: "Хобби и активности",
  work_style_and_environment: "Стиль работы",
  behavioral_situations: "Ситуации и поведение",
  mini_cognitive_tasks: "Мини-задачи",
};

export default function TestPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isAllowed, setIsAllowed] = useState(false);
  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | number | undefined>();
  const [selectedMulti, setSelectedMulti] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [completing, setCompleting] = useState(false);

  useEffect(() => {
    const entryRoute = getTestEntryRoute();
    if (entryRoute !== "/test") {
      router.replace(entryRoute);
      return;
    }
    setIsAllowed(true);
  }, [router]);

  const startTest = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await authFetch("/assessments/start", {
        method: "POST",
        headers: getAuthHeaders(true),
        body: JSON.stringify({ assessment_slug: "express_v1" }),
      });
      if (!res.ok) {
        const body = await res.text();
        throw new Error(`Не удалось создать сессию (${res.status}): ${body}`);
      }
      const payload = await res.json();
      const sid = payload.session_id;
      setSessionId(sid);

      const qRes = await fetch(`${apiUrl}/assessments/${sid}/questions`);
      if (!qRes.ok) {
        throw new Error("Не удалось загрузить вопросы");
      }
      const qPayload = await qRes.json();
      setQuestions(qPayload.questions);
      setCurrentIndex(0);
      setSelectedAnswer(undefined);
    } catch (err) {
      if (err instanceof AuthExpiredError) {
        return;
      }
      setError(err instanceof Error ? err.message : "Ошибка при создании сессии");
    } finally {
      setLoading(false);
    }
  }, []);

  const currentQuestion = questions[currentIndex];
  const totalQuestions = questions.length;

  const isMulti = currentQuestion?.question_type === "multi_select";
  const hasAnswer = isMulti ? selectedMulti.length > 0 : selectedAnswer !== undefined;

  const toggleMulti = useCallback((key: string) => {
    setSelectedMulti((prev) => {
      if (prev.includes(key)) return prev.filter((k) => k !== key);
      if (prev.length >= 3) return prev;
      return [...prev, key];
    });
  }, []);

  const handleNext = useCallback(async () => {
    if (!hasAnswer || !sessionId || !currentQuestion) return;

    setSubmitting(true);
    try {
      let answer: Record<string, unknown>;
      if (currentQuestion.question_type === "likert") {
        answer = { value: selectedAnswer };
      } else if (currentQuestion.question_type === "multi_select") {
        answer = { keys: selectedMulti };
      } else {
        answer = { key: selectedAnswer };
      }

      const res = await authFetch(`/assessments/${sessionId}/answer`, {
        method: "POST",
        headers: getAuthHeaders(true),
        body: JSON.stringify({
          question_id: currentQuestion.question_id,
          answer,
        }),
      });
      if (!res.ok) {
        throw new Error("Ошибка при отправке ответа");
      }

      if (currentIndex < totalQuestions - 1) {
        setCurrentIndex((prev) => prev + 1);
        setSelectedAnswer(undefined);
        setSelectedMulti([]);
      } else {
        setCompleting(true);
        const completeRes = await authFetch(`/assessments/${sessionId}/complete`, {
          method: "POST",
          headers: getAuthHeaders(),
        });
        if (!completeRes.ok) {
          throw new Error("Ошибка при завершении теста");
        }
        const completePayload = await completeRes.json();
        router.push(`/results?result_id=${completePayload.result_id}`);
      }
    } catch (err) {
      if (err instanceof AuthExpiredError) {
        return;
      }
      setError(err instanceof Error ? err.message : "Ошибка");
    } finally {
      setSubmitting(false);
      setCompleting(false);
    }
  }, [selectedAnswer, selectedMulti, hasAnswer, sessionId, currentQuestion, currentIndex, totalQuestions, router]);

  const handleBack = useCallback(() => {
    if (currentIndex <= 0) return;
    setCurrentIndex((prev) => prev - 1);
    setSelectedAnswer(undefined);
    setSelectedMulti([]);
  }, [currentIndex]);

  if (!isAllowed) return null;

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />

      <FocusedTaskLayout>
        {sessionId && questions.length > 0 && currentQuestion ? (
          <>
            <AssessmentHeader
              sectionLabel={blockLabels[currentQuestion.block] || currentQuestion.block}
              currentStep={currentIndex + 1}
              totalSteps={totalQuestions}
            />
            <ProgressBar
              value={currentIndex + 1}
              max={totalQuestions}
              className="test-question-progress"
            />

            <QuestionCard>
              <h2>{currentQuestion.text}</h2>
              <div className="question-options">
                {currentQuestion.question_type === "likert" ? (
                  currentQuestion.options.map((opt) => (
                    <AnswerOptionRow
                      key={String(opt.value)}
                      selected={selectedAnswer === opt.value}
                      onClick={() => setSelectedAnswer(opt.value)}
                    >
                      {opt.label}
                    </AnswerOptionRow>
                  ))
                ) : currentQuestion.question_type === "multi_select" ? (
                  currentQuestion.options.map((opt) => (
                    <AnswerOptionRow
                      key={opt.key}
                      selected={selectedMulti.includes(opt.key ?? "")}
                      onClick={() => toggleMulti(opt.key ?? "")}
                    >
                      {opt.label}
                      {selectedMulti.includes(opt.key ?? "") && " ✓"}
                    </AnswerOptionRow>
                  ))
                ) : (
                  currentQuestion.options.map((opt) => (
                    <AnswerOptionRow
                      key={opt.key}
                      selected={selectedAnswer === opt.key}
                      onClick={() => setSelectedAnswer(opt.key)}
                    >
                      {opt.label}
                    </AnswerOptionRow>
                  ))
                )}
              </div>
              {isMulti && (
                <p style={{ marginTop: 8, fontSize: 14, color: "#888" }}>
                  Выбрано: {selectedMulti.length} из 3
                </p>
              )}
            </QuestionCard>

            {error && <div className="test-start-message test-start-message-error">{error}</div>}

            <div className="assessment-actions">
              <button
                type="button"
                className="assessment-back-btn"
                onClick={handleBack}
                disabled={currentIndex <= 0 || submitting}
              >
                <span aria-hidden>‹</span>
                Назад
              </button>
              <button
                type="button"
                className="assessment-next-btn"
                onClick={handleNext}
                disabled={!hasAnswer || submitting || completing}
              >
                {completing
                  ? "Завершаем..."
                  : submitting
                    ? "Отправка..."
                    : currentIndex === totalQuestions - 1
                      ? "Завершить"
                      : "Далее"}
                <span aria-hidden>›</span>
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="test-start-surface">
              <p className="test-start-kicker">Тест CareerPath</p>
              <h1>24 вопроса, чтобы понять себя</h1>
              <p>
                Это экспресс-тест из 24 вопросов: быстро пройдите оценку и
                получите персональные рекомендации.
              </p>

              <div className="test-start-header">
                <button
                  onClick={startTest}
                  className="test-start-btn"
                  disabled={loading}
                >
                  {loading ? "Загрузка..." : "Начать тест"}
                </button>
              </div>

              {error && (
                <div className="test-start-message test-start-message-error">{error}</div>
              )}
            </div>
          </>
        )}
      </FocusedTaskLayout>

      <SiteFooter />
    </div>
  );
}
