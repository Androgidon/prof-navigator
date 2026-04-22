"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { FocusedTaskLayout } from "@/components/layout/focused-task-layout";
import { ProgressBar } from "@/components/layout/progress-bar";
import { setAccountEmail, setPendingVerificationEmail } from "@/lib/auth-flow";

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export default function RegisterPage() {
  const router = useRouter();
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage(null);

    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email") ?? "").trim();
    const password = String(formData.get("password") ?? "");
    const confirmPassword = String(formData.get("confirmPassword") ?? "");

    if (!password || !confirmPassword) {
      setStatus("error");
      setMessage("Заполните оба поля пароля");
      return;
    }

    if (password.length < 8 || confirmPassword.length < 8) {
      setStatus("error");
      setMessage("Пароль должен быть не менее 8 символов");
      return;
    }

    if (password !== confirmPassword) {
      setStatus("error");
      setMessage("Пароли не совпадают");
      return;
    }

    setStatus("loading");

    const payload = {
      email,
      password,
      confirm_password: confirmPassword,
    };

    try {
      const response = await fetch(`${apiBase}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const detail = String(errorData?.detail ?? "");
        if (detail.includes("завершите подтверждение")) {
          setPendingVerificationEmail(email);
          router.push("/verify-email");
          return;
        }
        throw new Error(detail || "Не удалось зарегистрироваться");
      }
      
      const data = await response.json();

      if (data.status === "registered" && data.access_token && data.refresh_token) {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        setAccountEmail(String(data.email ?? payload.email ?? ""));
        setStatus("success");
        setMessage("Регистрация прошла успешно. Перенаправление...");
        setTimeout(() => {
          router.push("/onboarding");
        }, 700);
        return;
      }

      setPendingVerificationEmail(String(data.email ?? payload.email ?? ""));
      setStatus("success");
      setMessage("Код подтверждения отправлен на email. Перенаправление...");

      setTimeout(() => {
        router.push("/verify-email");
      }, 700);
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

            <div className="form-group">
              <label htmlFor="confirmPassword" className="form-label">Повторите пароль</label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                minLength={8}
                required
                className="form-input"
                placeholder="Повторите пароль"
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