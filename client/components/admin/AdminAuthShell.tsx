"use client";

import Image from "next/image";
import type { ReactNode } from "react";

interface AdminAuthShellProps {
  title: string;
  subtitle: string;
  children: ReactNode;
}

export function AdminAuthShell({ title, subtitle, children }: AdminAuthShellProps) {
  return (
    <div className="flex min-h-full flex-1 flex-col bg-zinc-50 dark:bg-zinc-950">
      <div className="h-[12rem] bg-indigo-600 px-6 py-10 text-white shadow-lg sm:px-12">
        <div className="mx-auto mb-8 flex w-full max-w-5xl items-center gap-3">
          <Image
            src="/favicon-no-bg.png"
            alt="Unlocked"
            width={36}
            height={36}
            className="rounded-lg"
          />
          <div>
            <h1 className="text-2xl font-bold">{title}</h1>
            <p className="mt-1 text-sm text-indigo-100">{subtitle}</p>
          </div>
        </div>
      </div>

      <div className="flex flex-1 justify-center px-4 py-10 sm:px-12">
        <div className="relative bottom-20 min-h-[24rem] w-full max-w-md rounded-2xl bg-white p-10 shadow-xl dark:bg-zinc-900">
          {children}
        </div>
      </div>
    </div>
  );
}
