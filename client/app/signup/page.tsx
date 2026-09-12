"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { AuthShell } from "@/components/auth/AuthShell";
import { MicButton } from "@/components/auth/MicButton";
import { ApiError, clientSignup, clientVerifySignup } from "@/lib/api";
import { saveTokens } from "@/lib/auth-storage";
import { useSpeechToText } from "@/lib/useSpeechToText";

type FieldKey = "first_name" | "last_name" | "phone_number";
type Step = "details" | "otp" | "success";

const FIELD_ORDER: FieldKey[] = ["first_name", "last_name", "phone_number"];
const FIELD_LABEL: Record<FieldKey, string> = {
  first_name: "First name",
  last_name: "Last name",
  phone_number: "Phone number",
};
const FIELD_PROMPT: Record<FieldKey, string> = {
  first_name: "Please state your first name.",
  last_name: "Please state your last name.",
  phone_number: "Please state your phone number, digit by digit.",
};

export default function SignupPage() {
  const [voiceMode, setVoiceMode] = useState(true);
  const [step, setStep] = useState<Step>("details");

  const [values, setValues] = useState<Record<FieldKey, string>>({
    first_name: "",
    last_name: "",
    phone_number: "",
  });
  const [activeField, setActiveField] = useState<FieldKey>("first_name");

  const [otpCode, setOtpCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const nextEmptyField = useMemo(
    () => FIELD_ORDER.find((key) => !values[key].trim()) ?? null,
    [values]
  );

  const { isListening, supported, start, stop } = useSpeechToText((transcript) => {
    const cleaned =
      activeField === "phone_number"
        ? transcript.replace(/[^\d+]/g, "")
        : transcript.trim();

    setValues((prev) => ({ ...prev, [activeField]: cleaned }));

    const next = FIELD_ORDER.find(
      (key) => key !== activeField && !values[key].trim()
    );
    if (next) setActiveField(next);
  });

  function handleMicTap() {
    if (isListening) {
      stop();
      return;
    }
    setActiveField(nextEmptyField ?? activeField);
    start();
  }

  const allFieldsFilled = FIELD_ORDER.every((key) => values[key].trim());

  async function handleContinue() {
    setError(null);
    setLoading(true);
    try {
      await clientSignup(values);
      setStep("otp");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function handleVerify(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await clientVerifySignup(values.phone_number, otpCode);
      saveTokens(tokens);
      setStep("success");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  if (step === "success") {
    return (
      <AuthShell title="Verify Identity" subtitle="Step 2 of 2: Complete" progress={1}>
        <div className="space-y-4 text-center">
          <p className="text-lg font-semibold text-emerald-600">You&apos;re all set.</p>
          <p className="text-sm text-zinc-500">
            Welcome, {values.first_name} {values.last_name}.
          </p>
          <Link href="/login" className="btn-primary inline-block">
            Continue to sign in
          </Link>
        </div>
      </AuthShell>
    );
  }

  if (step === "otp") {
    return (
      <AuthShell
        title="Verify Identity"
        subtitle="Step 2 of 2: Verify your phone"
        progress={1}
      >
        <form onSubmit={handleVerify} className="space-y-4">
          <p className="text-sm text-zinc-500">
            Enter the code sent to <span className="font-medium">{values.phone_number}</span>
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
            {loading ? "Verifying…" : "Verify & continue"}
          </button>
        </form>
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title="Verify Identity"
      subtitle="Step 1 of 2: Personal details"
      voiceMode={voiceMode}
      onToggleVoiceMode={() => setVoiceMode((v) => !v)}
      progress={0.5}
    >
      {voiceMode && (
        <div className="mb-5 rounded-xl bg-indigo-50 p-3 dark:bg-indigo-950/40">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-indigo-500">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-900">
              🔊
            </span>
            Assistant prompt
          </div>
          <p className="mt-2 text-sm font-medium text-zinc-700 dark:text-zinc-200">
            &ldquo;{FIELD_PROMPT[nextEmptyField ?? activeField]}&rdquo;
          </p>
          {isListening && (
            <div className="mt-2 flex items-center gap-2 text-xs text-indigo-500">
              <span className="h-2 w-2 animate-ping rounded-full bg-indigo-500" />
              Listening…
              <span className="ml-auto rounded bg-indigo-100 px-1.5 py-0.5 font-semibold dark:bg-indigo-900">
                LIVE
              </span>
            </div>
          )}
          {!supported && (
            <p className="mt-2 text-xs text-amber-600">
              Voice input isn&apos;t supported in this browser — try Chrome or Edge, or switch
              off voice mode.
            </p>
          )}
        </div>
      )}

      <div className="space-y-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-indigo-500">
          01 Personal information
        </p>
        {FIELD_ORDER.map((key) => (
          <label key={key} className="block">
            <span className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
              {FIELD_LABEL[key]}
            </span>
            <input
              type={key === "phone_number" ? "tel" : "text"}
              value={values[key]}
              onFocus={() => setActiveField(key)}
              onChange={(e) => setValues((prev) => ({ ...prev, [key]: e.target.value }))}
              placeholder={key === "phone_number" ? "+254712345678" : "e.g. Sheldon"}
              className={`input mt-1 ${activeField === key && voiceMode ? "ring-2 ring-indigo-200" : ""}`}
            />
          </label>
        ))}
      </div>

      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}

      <div className="mt-6 flex items-center justify-between text-xs">
        <Link href="/login" className="font-semibold text-zinc-400">
          Already have an account?
        </Link>
        <button
          type="button"
          onClick={() => setVoiceMode((v) => !v)}
          className="rounded-full bg-zinc-100 px-3 py-1 font-semibold text-zinc-500 dark:bg-zinc-800"
        >
          {voiceMode ? "Manual mode" : "Voice mode"}
        </button>
      </div>

      {voiceMode ? (
        <div className="mt-6 flex flex-col items-center gap-3">
          <MicButton
            isListening={isListening}
            disabled={!supported}
            onClick={handleMicTap}
            hint="Tap to speak, tap again to stop"
          />
          {allFieldsFilled && (
            <button
              type="button"
              onClick={handleContinue}
              disabled={loading}
              className="btn-primary w-full"
            >
              {loading ? "Submitting…" : "Continue →"}
            </button>
          )}
        </div>
      ) : (
        <button
          type="button"
          onClick={handleContinue}
          disabled={loading || !allFieldsFilled}
          className="btn-primary mt-6 w-full"
        >
          {loading ? "Submitting…" : "Continue →"}
        </button>
      )}
    </AuthShell>
  );
}
