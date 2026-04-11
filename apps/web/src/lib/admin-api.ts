import { authFetch } from "@/lib/api-client";

export async function adminFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await authFetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const error = new Error(payload?.detail?.message ?? payload?.detail ?? "Request failed") as Error & {
      status?: number;
      code?: string;
    };
    error.status = response.status;
    error.code = payload?.detail?.code;
    throw error;
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}
