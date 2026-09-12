"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { DecodedToken } from "@/lib/auth-storage";
import { clearTokens } from "@/lib/auth-storage";

interface NavItem {
  label: string;
  href: string;
  enabled: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Applications", href: "/admin/dashboard", enabled: true },
  { label: "Block Catalog", href: "/admin/blocks", enabled: true },
  { label: "Sessions & Users", href: "/admin/sessions", enabled: false },
  { label: "Audit Log", href: "/admin/audit-log", enabled: false },
];

export function AdminSidebar({ admin }: { admin: DecodedToken | null }) {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    clearTokens();
    router.replace("/admin/login");
  }

  return (
    <aside className="flex w-56 shrink-0 flex-col justify-between border-r border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
      <div>
        <div className="mb-6 flex items-center gap-2 px-2">
          <Image
            src="/favicon-no-bg.png"
            alt="Unlocked"
            width={28}
            height={28}
            className="rounded-lg"
          />
          <span className="font-bold text-zinc-900 dark:text-zinc-50">Unlocked</span>
        </div>

        <nav className="space-y-1">
          {NAV_ITEMS.map((item) =>
            item.enabled ? (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  pathname === item.href
                    ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-950/50 dark:text-indigo-300"
                    : "text-zinc-600 hover:bg-zinc-50 dark:text-zinc-300 dark:hover:bg-zinc-800"
                }`}
              >
                {item.label}
              </Link>
            ) : (
              <span
                key={item.href}
                title="Not implemented yet — no backend endpoint for this"
                className="flex items-center justify-between rounded-lg px-3 py-2 text-sm font-medium text-zinc-300 dark:text-zinc-600"
              >
                {item.label}
                <span className="text-[10px] uppercase">Soon</span>
              </span>
            )
          )}

          {admin?.role === "super_admin" && (
            <Link
              href="/admin/signup"
              className={`block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                pathname === "/admin/signup"
                  ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-950/50 dark:text-indigo-300"
                  : "text-zinc-600 hover:bg-zinc-50 dark:text-zinc-300 dark:hover:bg-zinc-800"
              }`}
            >
              Admin Signup
            </Link>
          )}
        </nav>
      </div>

      <div className="space-y-2 border-t border-zinc-100 pt-4 dark:border-zinc-800">
        <p className="px-2 text-xs text-zinc-400">
          Signed in as <span className="font-semibold text-zinc-500">{admin?.role}</span>
        </p>
        <button
          type="button"
          onClick={handleLogout}
          className="w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30"
        >
          Log out
        </button>
      </div>
    </aside>
  );
}
