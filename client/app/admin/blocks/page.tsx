"use client";

import { useEffect, useState } from "react";
import { AdminSidebar } from "@/components/admin/AdminSidebar";
import { ApiError, type KYCBlockDefinition, listBlockCatalog } from "@/lib/api";
import { getAccessToken } from "@/lib/auth-storage";
import { useRequireAdmin } from "@/lib/useRequireAdmin";

export default function BlockCatalogPage() {
  const { admin, checked } = useRequireAdmin();
  const [blocks, setBlocks] = useState<KYCBlockDefinition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!checked) return;
    const token = getAccessToken();
    if (!token) return;

    listBlockCatalog(token)
      .then(setBlocks)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [checked]);

  if (!checked) return null;

  return (
    <div className="flex min-h-full bg-zinc-50 dark:bg-zinc-950">
      <AdminSidebar admin={admin} />

      <main className="flex-1 p-8">
        <h1 className="mb-1 text-xl font-bold text-zinc-900 dark:text-zinc-50">Block Catalog</h1>
        <p className="mb-6 text-sm text-zinc-400">
          Read-only — the KYC building blocks available to assign to an app&apos;s pipeline.
        </p>

        {loading && <p className="text-sm text-zinc-400">Loading…</p>}
        {error && <p className="text-sm text-red-600">{error}</p>}

        <div className="overflow-x-auto rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-zinc-200 text-xs uppercase tracking-wide text-zinc-400 dark:border-zinc-800">
              <tr>
                <th className="px-4 py-3">Code</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Channels</th>
                <th className="px-4 py-3">Version</th>
              </tr>
            </thead>
            <tbody>
              {blocks.map((block) => (
                <tr key={block.id} className="border-b border-zinc-100 last:border-0 dark:border-zinc-800">
                  <td className="px-4 py-3 font-medium text-zinc-900 dark:text-zinc-50">
                    {block.code}
                  </td>
                  <td className="px-4 py-3 text-zinc-500">{block.category}</td>
                  <td className="px-4 py-3 text-zinc-500">{block.supports_channels.join(", ")}</td>
                  <td className="px-4 py-3 text-zinc-500">v{block.version}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
