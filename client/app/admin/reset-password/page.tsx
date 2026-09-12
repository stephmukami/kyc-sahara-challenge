"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { AuthShell } from "@/components/auth/AuthShell";
import { ApiError, adminResetPassword } from "@/lib/api";

function ResetPasswordForm() {
  const router = useRouter();
  const token = useSearchParams().get("token") ?? "";

  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await adminResetPassword(token, newPassword);
      setDone(true);
      setTimeout(() => router.push("/login"), 1500);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell title="Set New Password" subtitle="Choose a new password for your account">
      {!token && (
        <p className="mb-4 text-sm text-amber-600">
          No reset token found in the link — paste it below manually if you have it.
        </p>
      )}
      {done ? (
        <p className="text-center text-sm font-medium text-emerald-600">
          Password reset — redirecting to sign in…
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block">
            <span className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
              New password
            </span>
            <input
              type="password"
              required
              minLength={8}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="••••••••"
              className="input mt-1"
            />
          </label>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "Resetting…" : "Reset password"}
          </button>
          <Link href="/login" className="block text-center text-xs font-semibold text-zinc-400">
            Back to sign in
          </Link>
        </form>
      )}
    </AuthShell>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={null}>
      <ResetPasswordForm />
    </Suspense>
  );
}
