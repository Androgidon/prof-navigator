"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { getAdminMe } from "@/lib/admin-rbac";
import { AuthExpiredError } from "@/lib/api-client";

export function AdminGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [state, setState] = useState<"loading" | "ready">("loading");

  useEffect(() => {
    let active = true;

    const run = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          router.replace("/login");
          return;
        }

        let me = null;
        try {
          me = await getAdminMe();
        } catch (error) {
          if (error instanceof AuthExpiredError) {
            return;
          }
        }

        if (!me || me.role !== "admin" || !me.is_active) {
          if (pathname !== "/admin/forbidden") {
            router.replace("/admin/forbidden");
            return;
          }
          if (active) {
            setState("ready");
          }
          return;
        }

        if (pathname === "/admin/forbidden") {
          router.replace("/admin");
          return;
        }

        if (active) {
          setState("ready");
        }
      } catch {
        if (pathname !== "/admin/forbidden") {
          router.replace("/admin/forbidden");
          return;
        }
        if (active) {
          setState("ready");
        }
      }
    };

    void run();
    return () => {
      active = false;
    };
  }, [pathname, router]);

  if (state === "loading") {
    return <div className="admin-loading">Проверка доступа...</div>;
  }

  return <>{children}</>;
}
