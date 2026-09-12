import type { TokenResponse } from "./api";

const ACCESS_TOKEN_KEY = "kyc_access_token";
const REFRESH_TOKEN_KEY = "kyc_refresh_token";

// Mirrored into a plain (non-httpOnly) cookie so `proxy.ts` can do a coarse
// "is there a session at all" check before a protected page even renders.
// The real check is still the FastAPI backend rejecting bad/missing tokens.
const SESSION_COOKIE = "kyc_session";

export interface DecodedToken {
  sub: string;
  role: string;
  type: "access" | "refresh";
  exp: number;
}

export function saveTokens(tokens: TokenResponse) {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  document.cookie = `${SESSION_COOKIE}=1; path=/; max-age=2592000; samesite=lax`;
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  document.cookie = `${SESSION_COOKIE}=; path=/; max-age=0`;
}

export function decodeToken(token: string): DecodedToken | null {
  try {
    const payload = token.split(".")[1];
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(normalized)) as DecodedToken;
  } catch {
    return null;
  }
}

export function getCurrentAdmin(): DecodedToken | null {
  const token = getAccessToken();
  if (!token) return null;
  const decoded = decodeToken(token);
  if (!decoded || decoded.role === "end_user") return null;
  return decoded;
}
