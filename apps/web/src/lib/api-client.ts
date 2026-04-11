import { clearAuthStorage, rememberPostLoginRedirect } from "@/lib/auth-flow";

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class AuthExpiredError extends Error {
  constructor(message = "Сессия истекла") {
    super(message);
    this.name = "AuthExpiredError";
  }
}

function toPath(input: string): string {
  if (input.startsWith("http://") || input.startsWith("https://")) {
    return input;
  }
  return `${apiBase}${input}`;
}

async function refreshAccessToken(): Promise<string | null> {
  if (typeof window === "undefined") {
    return null;
  }
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) {
    return null;
  }

  try {
    const response = await fetch(`${apiBase}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!response.ok) {
      return null;
    }
    const payload = (await response.json()) as {
      access_token: string;
      refresh_token: string;
    };
    localStorage.setItem("access_token", payload.access_token);
    localStorage.setItem("refresh_token", payload.refresh_token);
    window.dispatchEvent(new Event("careerpath:auth-changed"));
    return payload.access_token;
  } catch {
    return null;
  }
}

function triggerAutoLogout(): never {
  if (typeof window !== "undefined") {
    const path = `${window.location.pathname}${window.location.search}`;
    rememberPostLoginRedirect(path);
    clearAuthStorage();
    if (window.location.pathname !== "/login") {
      window.location.replace("/login");
    }
  }
  throw new AuthExpiredError();
}

type AuthFetchOptions = {
  redirectOnAuthError?: boolean;
};

export async function authFetch(path: string, init?: RequestInit, options?: AuthFetchOptions): Promise<Response> {
  const redirectOnAuthError = options?.redirectOnAuthError ?? true;

  const requestWithToken = async (token: string | null): Promise<Response> => {
    return fetch(toPath(path), {
      ...init,
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(init?.headers ?? {}),
      },
    });
  };

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  let response = await requestWithToken(token);

  if (response.status !== 401) {
    return response;
  }

  const refreshed = await refreshAccessToken();
  if (!refreshed) {
    if (redirectOnAuthError) {
      triggerAutoLogout();
    }
    throw new AuthExpiredError();
  }

  response = await requestWithToken(refreshed);
  if (response.status === 401) {
    if (redirectOnAuthError) {
      triggerAutoLogout();
    }
    throw new AuthExpiredError();
  }

  return response;
}
