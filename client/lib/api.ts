const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (typeof body?.detail === "string") detail = body.detail;
    } catch {
      // response wasn't JSON — fall back to statusText
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

function authHeader(accessToken: string): HeadersInit {
  return { Authorization: `Bearer ${accessToken}` };
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface MessageResponse {
  detail: string;
}

export type AdminRole = "super_admin" | "app_admin";

export interface AdminRead {
  id: string;
  email: string;
  role: AdminRole;
  created_at: string;
}

export interface AppRead {
  id: string;
  name: string;
  slug: string;
  status: "active" | "inactive";
  allowed_channels: string[];
  phone_trigger_number: string | null;
  default_language: string;
  webhook_url: string | null;
  created_by_id: string;
  created_at: string;
  updated_at: string;
}

export interface AppListItem extends AppRead {
  active_session_count: number;
}

export interface KYCBlockDefinition {
  id: string;
  code: string;
  category: string;
  supports_channels: string[];
  input_schema: Record<string, unknown>;
  default_config: Record<string, unknown>;
  version: number;
}

export interface AppBlockConfig {
  id: string;
  order_index: number;
  is_required: boolean;
  is_enabled: boolean;
  config_overrides: Record<string, unknown>;
  block: KYCBlockDefinition;
}

// ---- Admin auth ----

export const adminLogin = (email: string, password: string) =>
  apiFetch<TokenResponse>("/admin/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

export const adminSignup = (
  accessToken: string,
  payload: { email: string; password: string; role: AdminRole }
) =>
  apiFetch<AdminRead>("/admin/auth/signup", {
    method: "POST",
    headers: authHeader(accessToken),
    body: JSON.stringify(payload),
  });

export const adminForgotPassword = (email: string) =>
  apiFetch<MessageResponse>("/admin/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email }),
  });

export const adminResetPassword = (token: string, new_password: string) =>
  apiFetch<MessageResponse>("/admin/auth/reset-password", {
    method: "POST",
    body: JSON.stringify({ token, new_password }),
  });

// ---- Client (end-user) auth ----

export const clientSignup = (payload: {
  phone_number: string;
  first_name: string;
  last_name: string;
}) =>
  apiFetch<MessageResponse>("/client/auth/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const clientVerifySignup = (phone_number: string, otp_code: string) =>
  apiFetch<TokenResponse>("/client/auth/signup/verify", {
    method: "POST",
    body: JSON.stringify({ phone_number, otp_code }),
  });

export const clientLogin = (phone_number: string) =>
  apiFetch<MessageResponse>("/client/auth/login", {
    method: "POST",
    body: JSON.stringify({ phone_number }),
  });

export const clientVerifyLogin = (phone_number: string, otp_code: string) =>
  apiFetch<TokenResponse>("/client/auth/login/verify", {
    method: "POST",
    body: JSON.stringify({ phone_number, otp_code }),
  });

// ---- Admin apps (existing, pre-auth endpoints) ----

export const listApps = (accessToken: string) =>
  apiFetch<AppListItem[]>("/admin/apps", { headers: authHeader(accessToken) });

export const listBlockCatalog = (accessToken: string) =>
  apiFetch<KYCBlockDefinition[]>("/admin/kyc-blocks", { headers: authHeader(accessToken) });

export const listAppBlocks = (accessToken: string, appId: string) =>
  apiFetch<AppBlockConfig[]>(`/admin/apps/${appId}/blocks`, {
    headers: authHeader(accessToken),
  });

export const createApp = (
  accessToken: string,
  payload: { name: string; slug: string; created_by_id: string }
) =>
  apiFetch<AppRead>("/admin/apps", {
    method: "POST",
    headers: authHeader(accessToken),
    body: JSON.stringify({ ...payload, allowed_channels: ["app"] }),
  });
