"use client";

import Link from "next/link";
import { useState } from "react";
import { AuthShell } from "@/components/auth/AuthShell";
import { ApiError, clientLogin, clientVerifyLogin } from "@/lib/api";
import { saveTokens } from "@/lib/auth-storage";

type Step = "phone" | "otp" | "success";

export default function LoginPage() {
  const [step, setStep] = useState<Step>("phone");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handlePhoneSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await clientLogin(phoneNumber);
      setStep("otp");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function handleOtpSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await clientVerifyLogin(phoneNumber, otpCode);
      saveTokens(tokens);
      setStep("success");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell title="Welcome Back" subtitle="Sign in to your Unlocked account">
      {step === "phone" && (
        <form onSubmit={handlePhoneSubmit} className="space-y-4">
          <label className="block">
            <span className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
              Phone number
            </span>
            <input
              type="tel"
              required
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="+254712345678"
              className="input mt-1"
            />
          </label>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "Sending code…" : "Send code →"}
          </button>
          <p className="text-center text-xs text-zinc-400">
            Not registered?{" "}
            <Link href="/signup" className="font-semibold text-indigo-600">
              Sign up
            </Link>
          </p>
          <Link
            href="/admin/login"
            className="block text-center text-xs font-semibold text-zinc-400"
          >
            Admin? Sign in here
          </Link>
        </form>
      )}

      {step === "otp" && (
        <form onSubmit={handleOtpSubmit} className="space-y-4">
          <p className="text-sm text-zinc-500">
            Enter the code sent to <span className="font-medium">{phoneNumber}</span>
          </p>
          <label className="block">
            <span className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
              OTP code
            </span>
            <input
              inputMode="numeric"
              required
              value={otpCode}
              onChange={(e) => setOtpCode(e.target.value)}
              placeholder="123456"
              className="input mt-1 tracking-[0.5em]"
            />
          </label>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "Verifying…" : "Verify & sign in"}
          </button>
          <button
            type="button"
            onClick={() => setStep("phone")}
            className="w-full text-center text-xs font-semibold text-zinc-400"
          >
            Use a different number
          </button>
        </form>
      )}

      {step === "success" && (
        <div className="space-y-4 text-center">
          <p className="text-lg font-semibold text-emerald-600">You&apos;re signed in.</p>
          <p className="text-sm text-zinc-500">Welcome back, {phoneNumber}.</p>
        </div>
      )}
    </AuthShell>
  );
}
