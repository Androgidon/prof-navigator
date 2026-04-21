"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { FocusedTaskLayout } from "@/components/layout/focused-task-layout";
import { ProgressBar } from "@/components/layout/progress-bar";
import {
  clearPendingVerificationEmail,
  getPendingVerificationEmail,
  setAccountEmail,
} from "@/lib/auth-flow";

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export default function VerifyEmailPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [resendCooldown, setResendCooldown] = useState(0);

  useEffect(() => {
    const pending = getPendingVerificationEmail();
    if (!pending) {
      router.replace("/register");
      return;
    }
    setEmail(pending);
  }, [router]);

  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = window.setInterval(() => {
      setResendCooldown((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [resendCooldown]);

  const verifyCode = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus("loading");
    setMessage(null);

    try {
      const response = await fetch(`${apiBase}/auth/verify-email-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code: code.trim() }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || "Не удалось подтвердить email");
      }

      const data = await response.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      setAccountEmail(email);
      clearPendingVerificationEmail();

      setStatus("success");
      setMessage("Email подтверждён. Перенаправление...");
      setTimeout(() => router.push("/onboarding"), 700);
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Ошибка подтверждения");
    }
  };

  const resendCode = async () => {
    if (!email || resendCooldown > 0) return;
    setMessage(null);

    try {
      const response = await fetch(`${apiBase}/auth/resend-email-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload?.detail || "Не удалось отправить код повторно");
      }

      const cooldown = Number(payload?.resend_available_in_seconds ?? 60);
      setResendCooldown(cooldown > 0 ? cooldown : 60);
      setMessage("Новый код отправлен на email");
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Ошибка отправки кода");
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <SiteHeader />
      <FocusedTaskLayout>
        <ProgressBar value={20} max={100} />
        <div className="auth-form-surface">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary mb-3">Подтверждение Email</p>
          <h1>Введите код из письма</h1>
          <p>Мы отправили 6-значный код на <strong>{email || "ваш email"}</strong>.</p>

          <form onSubmit={verifyCode}>
            <div className="form-group">
              <label htmlFor="code" className="form-label">Код подтверждения</label>
              <input
                id="code"
                name="code"
                type="text"
                inputMode="numeric"
                pattern="[0-9]{6}"
                minLength={6}
                maxLength={6}
                required
                className="form-input"
                placeholder="123456"
                value={code}
                onChange={(event) => setCode(event.target.value.replace(/\D/g, "").slice(0, 6))}
              />
            </div>

            <button type="submit" className="form-submit-btn" disabled={status === "loading"}>
              {status === "loading" ? "Проверка..." : "Подтвердить email"}
            </button>

            <button
              type="button"
              className="form-submit-btn mt-3"
              onClick={resendCode}
              disabled={resendCooldown > 0}
            >
              {resendCooldown > 0 ? `Отправить код повторно через ${resendCooldown}с` : "Отправить код повторно"}
            </button>

            {message && (
              <p className={`form-message ${status === "success" ? "form-message-success" : "form-message-error"}`}>
                {message}
              </p>
            )}
          </form>

          <p className="text-center text-sm text-muted-foreground mt-6">
            Неверный email? <Link href="/register" className="text-primary hover:underline">Вернуться к регистрации</Link>
          </p>
        </div>
      </FocusedTaskLayout>
      <SiteFooter />
    </div>
  );
}
