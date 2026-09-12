"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AuthShell } from "@/components/auth/AuthShell";
import { ApiError, adminLogin, clientLogin, clientVerifyLogin } from "@/lib/api";
import { saveTokens } from "@/lib/auth-storage";

type Tab = "admin" | "user";
type UserStep = "phone" | "otp" | "success";

export default function LoginPage() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("admin");

  // Admin form state
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [adminError, setAdminError] = useState<string | null>(null);
  const [adminLoading, setAdminLoading] = useState(false);

  // User (phone OTP) form state
  const [userStep, setUserStep] = useState<UserStep>("phone");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [userError, setUserError] = useState<string | null>(null);
  const [userLoading, setUserLoading] = useState(false);

  async function handleAdminSubmit(e: React.FormEvent) {
    e.preventDefault();
    setAdminError(null);
    setAdminLoading(true);
    try {
      const tokens = await adminLogin(email, password);
      saveTokens(tokens);
      router.push("/admin/dashboard");
    } catch (err) {
      setAdminError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setAdminLoading(false);
    }
  }

  async function handlePhoneSubmit(e: React.FormEvent) {
    e.preventDefault();
    setUserError(null);
    setUserLoading(true);
    try {
      await clientLogin(phoneNumber);
      setUserStep("otp");
    } catch (err) {
      setUserError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setUserLoading(false);
    }
  }

  async function handleOtpSubmit(e: React.FormEvent) {
    e.preventDefault();
    setUserError(null);
    setUserLoading(true);
    try {
      const tokens = await clientVerifyLogin(phoneNumber, otpCode);
      saveTokens(tokens);
      setUserStep("success");
    } catch (err) {
      setUserError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setUserLoading(false);
    }
  }

  return (
    <AuthShell title="Welcome Back" subtitle="Sign in to your KYC Orchestrator account">
      <div className="mb-6 flex rounded-full bg-zinc-100 p-1 dark:bg-zinc-800">
        <button
          type="button"
          onClick={() => setTab("admin")}
          className={`flex-1 rounded-full py-2 text-sm font-semibold transition-colors ${
            tab === "admin"
              ? "bg-white text-indigo-700 shadow dark:bg-zinc-700 dark:text-white"
              : "text-zinc-500"
          }`}
        >
          Admin
        </button>
        <button
          type="button"
          onClick={() => setTab("user")}
          className={`flex-1 rounded-full py-2 text-sm font-semibold transition-colors ${
            tab === "user"
              ? "bg-white text-indigo-700 shadow dark:bg-zinc-700 dark:text-white"
              : "text-zinc-500"
          }`}
        >
          User
        </button>
      </div>

      {tab === "admin" && (
        <form onSubmit={handleAdminSubmit} className="space-y-4">
          <Field label="Email address">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@domain.com"
              className="input"
            />
          </Field>
          <Field
            label="Password"
            action={
              <Link href="/admin/forgot-password" className="text-xs font-semibold text-indigo-600">
                Forgot?
              </Link>
            }
          >
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="input"
            />
          </Field>

          {adminError && <p className="text-sm text-red-600">{adminError}</p>}

          <button type="submit" disabled={adminLoading} className="btn-primary w-full">
            {adminLoading ? "Signing in…" : "Sign In →"}
          </button>
        </form>
      )}

      {tab === "user" && (
        <>
          {userStep === "phone" && (
            <form onSubmit={handlePhoneSubmit} className="space-y-4">
              <Field label="Phone number">
                <input
                  type="tel"
                  required
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="+254712345678"
                  className="input"
                />
              </Field>
              {userError && <p className="text-sm text-red-600">{userError}</p>}
              <button type="submit" disabled={userLoading} className="btn-primary w-full">
                {userLoading ? "Sending code…" : "Send code →"}
              </button>
              <p className="text-center text-xs text-zinc-400">
                Not registered?{" "}
                <Link href="/signup" className="font-semibold text-indigo-600">
                  Sign up
                </Link>
              </p>
            </form>
          )}

          {userStep === "otp" && (
            <form onSubmit={handleOtpSubmit} className="space-y-4">
              <p className="text-sm text-zinc-500">
                Enter the code sent to <span className="font-medium">{phoneNumber}</span>
              </p>
              <Field label="OTP code">
                <input
                  inputMode="numeric"
                  required
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  placeholder="123456"
                  className="input tracking-[0.5em]"
                />
              </Field>
              {userError && <p className="text-sm text-red-600">{userError}</p>}
              <button type="submit" disabled={userLoading} className="btn-primary w-full">
                {userLoading ? "Verifying…" : "Verify & sign in"}
              </button>
              <button
                type="button"
                onClick={() => setUserStep("phone")}
                className="w-full text-center text-xs font-semibold text-zinc-400"
              >
                Use a different number
              </button>
            </form>
          )}

          {userStep === "success" && (
            <div className="space-y-4 text-center">
              <p className="text-lg font-semibold text-emerald-600">You&apos;re signed in.</p>
              <p className="text-sm text-zinc-500">Welcome back, {phoneNumber}.</p>
            </div>
          )}
        </>
      )}
    </AuthShell>
  );
}

function Field({
  label,
  action,
  children,
}: {
  label: string;
  action?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="flex items-center justify-between text-xs font-semibold uppercase tracking-wide text-zinc-500">
        {label}
        {action}
      </span>
      <div className="mt-1">{children}</div>
    </label>
  );
}
