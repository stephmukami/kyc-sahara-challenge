import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Public even though they live under /admin/*
const PUBLIC_ADMIN_PATHS = ["/admin/login", "/admin/forgot-password", "/admin/reset-password"];

// This is only a coarse "is there a session at all" check so protected pages
// don't flash before redirecting — it can't verify the JWT (no secret here),
// so the real check is the FastAPI backend rejecting bad/missing tokens, and
// each protected page's own `useRequireAdmin()` role check.
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isAdminRoute = pathname.startsWith("/admin");
  const isPublicAdminPath = PUBLIC_ADMIN_PATHS.some((path) => pathname.startsWith(path));

  if (isAdminRoute && !isPublicAdminPath && !request.cookies.has("kyc_session")) {
    return NextResponse.redirect(new URL("/admin/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*"],
};
