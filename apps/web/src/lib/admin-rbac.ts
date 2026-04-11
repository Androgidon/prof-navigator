import { adminFetch } from "@/lib/admin-api";

export type AdminMe = {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
};

export async function getAdminMe(): Promise<AdminMe> {
  return adminFetch<AdminMe>("/admin/me");
}
