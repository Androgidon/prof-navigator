"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { FocusedTaskLayout } from "@/components/layout/focused-task-layout";
import { ProgressBar } from "@/components/layout/progress-bar";
import { setAccountEmail } from "@/lib/auth-flow";

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export default function RegisterPage() {
  const router = useRouter();
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus("loading");
    setMessage(null);
    
    const formData = new FormData(event.currentTarget);
    const payload = {
      email: formData.get("email"),
      password: formData.get("password"),
    };

    try {
      const response = await fetch(`${apiBase}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || "Не удалось зарегистрироваться");
      }
      
      const data = await response.json();
      
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      setAccountEmail(String(payload.email ?? ""));
      
      setStatus("success");
      setMessage("Регистрация прошла успешно. Перенаправление...");
      
      // Redirect to dashboard after short delay
      setTimeout(() => {
        router.push("/onboarding");
      }, 1000);
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Ошибка");
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />

      <FocusedTaskLayout>
        <ProgressBar value={0} max={100} />

        <div className="auth-form-surface">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">
            Регистрация
          </p>
          <h1>Создайте аккаунт CareerPath</h1>
          <p>
            Зарегистрируйтесь, чтобы начать тест, сохранить результаты и получить
            explainable рекомендации по профессиям.
          </p>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email" className="form-label">Email</label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="form-input"
                placeholder="your@email.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">Пароль</label>
              <input
                id="password"
                name="password"
                type="password"
                minLength={8}
                required
                className="form-input"
                placeholder="Минимум 8 символов"
              />
            </div>

            <button 
              type="submit" 
              className="form-submit-btn"
              disabled={status === "loading"}
            >
              {status === "loading" ? "Регистрация..." : "Зарегистрироваться"}
            </button>

            {status !== "idle" && status !== "loading" && (
              <p className={`form-message ${status === "success" ? "form-message-success" : "form-message-error"}`}>
                {message}
              </p>
            )}
          </form>

          <p className="text-center text-sm text-muted-foreground mt-6">
            Уже есть аккаунт?{" "}
            <Link href="/login" className="text-primary hover:underline">
              Войти
            </Link>
          </p>
        </div>
      </FocusedTaskLayout>

      <SiteFooter />
    </div>
  );
}