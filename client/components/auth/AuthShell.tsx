"use client";

import Image from "next/image";
import type { ReactNode } from "react";

interface AuthShellProps {
  title: string;
  subtitle: string;
  voiceMode?: boolean;
  onToggleVoiceMode?: () => void;
  progress?: number; // 0-1
  children: ReactNode;
}

export function AuthShell({
  title,
  subtitle,
  voiceMode,
  onToggleVoiceMode,
  progress,
  children,
}: AuthShellProps) {
  return (
    <div className="min-h-full flex flex-col items-center bg-zinc-100 px-4 py-10 dark:bg-zinc-950">
      <div className="w-full max-w-sm">
        <div className="rounded-t-3xl bg-gradient-to-br from-indigo-600 to-indigo-500 px-6 pt-6 pb-10 text-white shadow-lg">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              <Image
                src="/favicon-no-bg.png"
                alt="Unlocked"
                width={32}
                height={32}
                className="mt-0.5 rounded-lg"
              />
              <div>
                <h1 className="text-xl font-bold">{title}</h1>
                <p className="mt-1 text-sm text-indigo-100">{subtitle}</p>
              </div>
            </div>
            {onToggleVoiceMode && (
              <button
                type="button"
                onClick={onToggleVoiceMode}
                className={`flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold transition-colors ${
                  voiceMode ? "bg-white/25 text-white" : "bg-black/20 text-indigo-100"
                }`}
              >
                <span
                  className={`h-1.5 w-1.5 rounded-full ${voiceMode ? "bg-emerald-300" : "bg-zinc-400"}`}
                />
                VOICE MODE
              </button>
            )}
          </div>

          {progress !== undefined && (
            <div className="mt-5 h-1.5 w-full overflow-hidden rounded-full bg-white/20">
              <div
                className="h-full rounded-full bg-white transition-all"
                style={{ width: `${Math.round(progress * 100)}%` }}
              />
            </div>
          )}
        </div>

        <div className="-mt-5 rounded-t-3xl bg-white px-6 pb-8 pt-6 shadow-xl dark:bg-zinc-900">
          {children}
        </div>
      </div>
    </div>
  );
}
