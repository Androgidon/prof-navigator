"use client";

import { AdminGuard } from "@/components/admin/admin-guard";
import { AdminNav } from "@/components/admin/admin-nav";

export function AdminLayoutShell({ children }: { children: React.ReactNode }) {
  return (
    <AdminGuard>
      <div className="admin-shell">
        <aside className="admin-sidebar">
          <div className="admin-brand">CareerPath Admin</div>
          <AdminNav />
        </aside>
        <main className="admin-main">{children}</main>
      </div>
    </AdminGuard>
  );
}
