"use client";

import { FormEvent, useState } from "react";

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export default function RegisterPage() {
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus("idle");
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
        throw new Error("Не удалось зарегистрироваться");
      }
      setStatus("success");
      setMessage("Регистрация прошла успешно. Токен сохранён в localStorage.");
    } catch (error) {
      setStatus("error");
      setMessage(error instanceof Error ? error.message : "Ошибка" );
    }
  };

  return (
    <section className="mx-auto flex w-full max-w-4xl flex-col gap-8 px-6 py-16">
      <div className="space-y-4">
        <p className="text-xs uppercase tracking-[0.4em] text-amber-400">Регистрация</p>
        <h1 className="text-3xl font-semibold text-white">Создайте аккаунт CareerPath</h1>
        <p className="text-sm text-slate-300">
          Зарегистрируйтесь, чтобы начать тест, сохранить результаты и получить explainable рекомендации
          по профессиям.
        </p>
      </div>
      <form
        onSubmit={handleSubmit}
        className="rounded-3xl border border-white/10 bg-slate-900/60 p-6 shadow-md"
      >
        <div className="space-y-4">
          <label className="flex flex-col gap-2 text-sm">
            <span className="text-slate-400">Email</span>
            <input
              name="email"
              type="email"
              required
              className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none transition focus:border-amber-400"
            />
          </label>
          <label className="flex flex-col gap-2 text-sm">
            <span className="text-slate-400">Пароль</span>
            <input
              name="password"
              type="password"
              minLength={8}
              required
              className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none transition focus:border-amber-400"
            />
          </label>
        </div>
        <button
          type="submit"
          className="mt-6 w-full rounded-2xl bg-amber-400/90 px-6 py-3 text-sm font-semibold uppercase tracking-[0.4em] text-slate-950 transition hover:bg-amber-300"
        >
          Зарегистрироваться
        </button>
        {status !== "idle" && (
          <p className={`mt-4 text-sm ${status === "success" ? "text-emerald-400" : "text-rose-400"}`}>
            {message}
          </p>
        )}
      </form>
    </section>
  );
}
