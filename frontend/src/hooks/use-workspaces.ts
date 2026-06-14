"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createWorkspace,
  getDashboardSummary,
  listWorkspaces,
  type CreateWorkspacePayload,
} from "@/lib/api/workspaces";
import { hasStoredSession } from "@/lib/auth-storage";

export const workspacesQueryKey = ["workspaces"] as const;
export const dashboardSummaryQueryKey = ["dashboard", "summary"] as const;

export function useWorkspaces(enabled = true) {
  return useQuery({
    queryKey: workspacesQueryKey,
    queryFn: listWorkspaces,
    enabled: enabled && hasStoredSession(),
  });
}

export function useDashboardSummary(enabled = true) {
  return useQuery({
    queryKey: dashboardSummaryQueryKey,
    queryFn: getDashboardSummary,
    enabled: enabled && hasStoredSession(),
  });
}

export function useCreateWorkspace() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateWorkspacePayload) => createWorkspace(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workspacesQueryKey });
      queryClient.invalidateQueries({ queryKey: dashboardSummaryQueryKey });
    },
  });
}
