"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { FocusedTaskLayout } from "@/components/layout/focused-task-layout";
import { ProgressBar } from "@/components/layout/progress-bar";
import { consumePostLoginRedirect, setAccountEmail } from "@/lib/auth-flow";

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export default function LoginPage() {
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
      const response = await fetch(`${apiBase}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const detail = String(errorData?.detail ?? "").toLowerCase();
        if (response.status === 403 && detail.includes("подтвердите email")) {
          throw new Error("Подтвердите email перед входом. Код можно отправить повторно на экране подтверждения.");
        }
        if (response.status === 401 || detail.includes("invalid credentials")) {
          throw new Error("Пользователь с такими данными не зарегистрирован. Пожалуйста, пройдите регистрацию.");
        }
        throw new Error(errorData?.detail || "Неверный email или пароль");
      }
      
      const data = await response.json();
      
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      setAccountEmail(String(payload.email ?? ""));
      
      setStatus("success");
      setMessage("Вход выполнен успешно. Перенаправление...");
      
      const redirectPath = consumePostLoginRedirect();
      setTimeout(() => {
        router.push(redirectPath);
      }, 1000);
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Ошибка при входе");
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />

      <FocusedTaskLayout>
        <ProgressBar value={0} max={100} />

        <div className="auth-form-surface">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">
            Вход
          </p>
          <h1>Войдите в CareerPath</h1>
          <p>
            Войдите в свой аккаунт, чтобы продолжить тест, 
            просматривать результаты и рекомендации.
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
                required
                className="form-input"
                placeholder="Введите пароль"
              />
            </div>

            <button 
              type="submit" 
              className="form-submit-btn"
              disabled={status === "loading"}
            >
              {status === "loading" ? "Вход..." : "Войти"}
            </button>

            {status !== "idle" && status !== "loading" && (
              <p className={`form-message ${status === "success" ? "form-message-success" : "form-message-error"}`}>
                {message}
              </p>
            )}
          </form>

          <p className="text-center text-sm text-muted-foreground mt-6">
            Еще нет аккаунта?{" "}
            <Link href="/register" className="text-primary hover:underline">
              Зарегистрироваться
            </Link>
          </p>
        </div>
      </FocusedTaskLayout>

      <SiteFooter />
    </div>
  );
}
