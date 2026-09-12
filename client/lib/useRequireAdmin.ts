"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { type DecodedToken, getCurrentAdmin } from "./auth-storage";

export function useRequireAdmin(requireSuperAdmin = false) {
  const router = useRouter();
  const [admin, setAdmin] = useState<DecodedToken | null>(null);
  const [checked, setChecked] = useState(false);

  // The admin's identity lives in localStorage, which is only readable on
  // the client — it must resolve after mount (not during the lazy initial
  // render) so this matches the server-rendered pass and avoids a hydration
  // mismatch. That two-pass pattern requires an effect-triggered setState.
  useEffect(() => {
    const current = getCurrentAdmin();
    if (!current || (requireSuperAdmin && current.role !== "super_admin")) {
      router.replace("/login");
      return;
    }
    /* eslint-disable react-hooks/set-state-in-effect */
    setAdmin(current);
    setChecked(true);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [router, requireSuperAdmin]);

  return { admin, checked };
}
