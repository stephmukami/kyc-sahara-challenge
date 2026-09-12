"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AdminAuthShell } from "@/components/admin/AdminAuthShell";
import { ApiError, adminLogin } from "@/lib/api";
import { saveTokens } from "@/lib/auth-storage";

export default function AdminLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await adminLogin(email, password);
      saveTokens(tokens);
      router.push("/admin/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AdminAuthShell title="Admin Login" subtitle="Sign in to the Unlocked admin console">
      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block">
          <span className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
            Email address
          </span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="admin@domain.com"
            className="input mt-1 mb-3"
          />
        </label>

        <label className="block">
          <span className="flex items-center justify-between text-xs font-semibold uppercase tracking-wide text-zinc-500">
            Password
            <Link href="/admin/forgot-password" className="font-semibold text-indigo-600">
              Forgot?
            </Link>
          </span>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="input mt-1 mb-3"
          />
        </label>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? "Signing in…" : "Sign In →"}
        </button>

        <Link href="/login" className="block text-center text-xs font-semibold text-zinc-400">
          Not an admin? Sign in here
        </Link>
      </form>
    </AdminAuthShell>
  );
}
