"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
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
    <div className="flex min-h-full flex-1 flex-col bg-zinc-50 dark:bg-zinc-950">
      <div className="bg-indigo-600 px-6 py-10 text-white shadow-lg sm:px-12 h-[12rem]">
        <div className="mx-auto flex w-full max-w-5xl items-center gap-3 mb-8" >
          <Image
            src="/favicon-no-bg.png"
            alt="Unlocked"
            width={36}
            height={36}
            className="rounded-lg"
          />
          <div className="" >
            <h1 className="text-2xl font-bold">Admin Login</h1>
            <p className="mt-1 text-sm text-indigo-100">
              Sign in to the Unlocked admin console
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-1 justify-center px-4 py-10 sm:px-12">
        <div className=" relative bottom-20 w-full h-[24rem] max-w-md rounded-2xl bg-white p-10 shadow-xl dark:bg-zinc-900">
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
        </div>
      </div>
    </div>
  );
}
