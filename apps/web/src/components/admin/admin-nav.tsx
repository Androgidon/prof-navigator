"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/admin", label: "Обзор" },
  { href: "/admin/assessments", label: "Assessments" },
  { href: "/admin/questions", label: "Question Bank" },
  { href: "/admin/professions", label: "Professions" },
  { href: "/admin/matrix", label: "Matrix" },
  { href: "/admin/users", label: "Users" },
];

export function AdminNav() {
  const pathname = usePathname();

  return (
    <nav className="admin-nav">
      {navItems.map((item) => {
        const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
        return (
          <Link key={item.href} href={item.href} className={cn("admin-nav-link", isActive && "admin-nav-link-active")}>
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
