"use client";

import { useQuery } from "@tanstack/react-query";

import { getMyWorkspace } from "@/lib/api/workspaces";
import { hasStoredSession } from "@/lib/auth-storage";

export const userWorkspaceQueryKey = ["workspace", "me"] as const;

export function useUserWorkspace() {
  return useQuery({
    queryKey: userWorkspaceQueryKey,
    queryFn: getMyWorkspace,
    enabled: hasStoredSession(),
  });
}
