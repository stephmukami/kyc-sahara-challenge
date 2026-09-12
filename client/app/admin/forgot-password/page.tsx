"use client";

import Link from "next/link";
import { useState } from "react";
import { AuthShell } from "@/components/auth/AuthShell";
import { ApiError, adminForgotPassword } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await adminForgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell title="Reset Password" subtitle="We'll email you a reset link">
      {sent ? (
        <div className="space-y-4 text-center">
          <p className="text-sm text-zinc-600 dark:text-zinc-300">
            If an account with that email exists, a reset link has been sent.
          </p>
          <Link href="/login" className="btn-primary inline-block">
            Back to sign in
          </Link>
        </div>
      ) : (
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
              className="input mt-1"
            />
          </label>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "Sending…" : "Send reset link"}
          </button>
          <Link href="/login" className="block text-center text-xs font-semibold text-zinc-400">
            Back to sign in
          </Link>
        </form>
      )}
    </AuthShell>
  );
}
