"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AdminAuthShell } from "@/components/admin/AdminAuthShell";
import { ApiError, adminSignup, type AdminRole } from "@/lib/api";
import { getAccessToken } from "@/lib/auth-storage";
import { useRequireAdmin } from "@/lib/useRequireAdmin";

export default function AdminSignupPage() {
  const router = useRouter();
  const { checked } = useRequireAdmin(true);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<AdminRole>("app_admin");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [created, setCreated] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const accessToken = getAccessToken();
    if (!accessToken) {
      router.replace("/admin/login");
      return;
    }

    setError(null);
    setCreated(null);
    setLoading(true);
    try {
      const admin = await adminSignup(accessToken, { email, password, role });
      setCreated(admin.email);
      setEmail("");
      setPassword("");
      setRole("app_admin");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  if (!checked) return null;

  return (
    <AdminAuthShell title="Admin Signup" subtitle="Create a new admin account">
      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        <div className="space-y-4">
          <p className="text-xs text-zinc-400">
            Only fields the backend stores today (email, password, role) — a fuller profile form
            would need model changes first.
          </p>

          <label className="block">
            <span className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
              Email address
            </span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="new-admin@domain.com"
              className="input mt-1"
            />
          </label>

          <label className="block">
            <span className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
              Temporary password
            </span>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="input mt-1"
            />
          </label>

          <label className="block">
            <span className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
              Admin role
            </span>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as AdminRole)}
              className="input mt-1"
            >
              <option value="app_admin">App admin</option>
              <option value="super_admin">Super admin</option>
            </select>
          </label>
        </div>

        <div className="space-y-3">
          {error && <p className="text-sm text-red-600">{error}</p>}
          {created && (
            <p className="text-sm font-medium text-emerald-600">Created admin: {created}</p>
          )}

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "Creating…" : "Create admin →"}
          </button>
          <Link
            href="/admin/dashboard"
            className="block text-center text-xs font-semibold text-zinc-400"
          >
            ← Back to dashboard
          </Link>
        </div>
      </form>
    </AdminAuthShell>
  );
}
