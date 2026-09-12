"use client";

import { useCallback, useEffect, useState } from "react";
import { AdminSidebar } from "@/components/admin/AdminSidebar";
import { ApiError, type AppListItem, createApp, listApps, listAppBlocks } from "@/lib/api";
import { getAccessToken } from "@/lib/auth-storage";
import { useRequireAdmin } from "@/lib/useRequireAdmin";

export default function AdminDashboardPage() {
  const { admin, checked } = useRequireAdmin();
  const [apps, setApps] = useState<AppListItem[]>([]);
  const [blockCounts, setBlockCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const loadApps = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const list = await listApps(token);
      setApps(list);

      const counts = await Promise.all(
        list.map(async (app) => {
          try {
            const blocks = await listAppBlocks(token, app.id);
            return [app.id, blocks.length] as const;
          } catch {
            return [app.id, 0] as const;
          }
        })
      );
      setBlockCounts(Object.fromEntries(counts));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load applications");
    } finally {
      setLoading(false);
    }
  }, []);

  // Standard fetch-on-mount: loadApps sets `loading`/`apps` state itself
  // (safe — it's a data fetch, not a render-synchronization concern), but
  // the linter's static analysis flags the call site regardless.
  useEffect(() => {
    /* eslint-disable-next-line react-hooks/set-state-in-effect */
    if (checked) loadApps();
  }, [checked, loadApps]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const token = getAccessToken();
    if (!token || !admin) return;

    setCreating(true);
    setCreateError(null);
    try {
      await createApp(token, { name, slug, created_by_id: admin.sub });
      setName("");
      setSlug("");
      setShowCreate(false);
      await loadApps();
    } catch (err) {
      setCreateError(err instanceof ApiError ? err.message : "Failed to create app");
    } finally {
      setCreating(false);
    }
  }

  if (!checked) return null;

  return (
    <div className="flex min-h-full bg-zinc-50 dark:bg-zinc-950">
      <AdminSidebar admin={admin} />

      <main className="flex-1 p-8">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
            Applications Overview
          </h1>
          <button
            type="button"
            onClick={() => setShowCreate((v) => !v)}
            className="btn-primary"
          >
            + Create New App
          </button>
        </div>

        {showCreate && (
          <form
            onSubmit={handleCreate}
            className="mb-6 flex flex-wrap items-end gap-3 rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900"
          >
            <label className="block">
              <span className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                Name
              </span>
              <input
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Standard KYC Flow"
                className="input mt-1"
              />
            </label>
            <label className="block">
              <span className="text-xs font-semibold uppercase tracking-wide text-zinc-500">
                Slug
              </span>
              <input
                required
                pattern="^[a-z0-9-]+$"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                placeholder="standard-kyc"
                className="input mt-1"
              />
            </label>
            <button type="submit" disabled={creating} className="btn-primary">
              {creating ? "Creating…" : "Save"}
            </button>
            {createError && <p className="w-full text-sm text-red-600">{createError}</p>}
          </form>
        )}

        {loading && <p className="text-sm text-zinc-400">Loading applications…</p>}
        {error && <p className="text-sm text-red-600">{error}</p>}

        {!loading && !error && apps.length === 0 && (
          <p className="text-sm text-zinc-400">No applications yet — create one to get started.</p>
        )}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {apps.map((app) => (
            <div
              key={app.id}
              className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900"
            >
              <div className="mb-2 flex items-center justify-between">
                <h2 className="font-semibold text-zinc-900 dark:text-zinc-50">{app.name}</h2>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                    app.status === "active"
                      ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
                      : "bg-zinc-100 text-zinc-500 dark:bg-zinc-800"
                  }`}
                >
                  {app.status}
                </span>
              </div>
              <p className="mb-3 text-xs text-zinc-400">/{app.slug}</p>
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-500">
                  <span className="font-semibold text-zinc-900 dark:text-zinc-50">
                    {blockCounts[app.id] ?? "…"}
                  </span>{" "}
                  blocks configured
                </span>
                <span className="text-zinc-500">
                  <span className="font-semibold text-zinc-900 dark:text-zinc-50">
                    {app.active_session_count}
                  </span>{" "}
                  active sessions
                </span>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
