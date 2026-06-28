"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createObsidianVault,
  deleteObsidianVault,
  getObsidianSyncStatus,
  listObsidianVaults,
  syncObsidianVault,
} from "@/lib/api/obsidian";
import { useUserWorkspace } from "@/hooks/use-user-workspace";
import { hasStoredSession } from "@/lib/auth-storage";

export const obsidianVaultsQueryKey = ["obsidian", "vaults"] as const;

export function useObsidianVaults() {
  const { data: workspace } = useUserWorkspace();
  const workspaceId = workspace?.id;

  return useQuery({
    queryKey: [...obsidianVaultsQueryKey, workspaceId],
    queryFn: () => listObsidianVaults(workspaceId!),
    enabled: hasStoredSession() && Boolean(workspaceId),
    refetchInterval: 10_000,
  });
}

export function useCreateObsidianVault() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createObsidianVault,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: obsidianVaultsQueryKey });
    },
  });
}

export function useSyncObsidianVault() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ vaultId, files }: { vaultId: string; files: File[] }) =>
      syncObsidianVault(vaultId, files),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: obsidianVaultsQueryKey });
    },
  });
}

export function useObsidianSyncStatus(vaultId: string | null, enabled = false) {
  return useQuery({
    queryKey: ["obsidian", "sync-status", vaultId],
    queryFn: () => getObsidianSyncStatus(vaultId!),
    enabled: enabled && Boolean(vaultId) && hasStoredSession(),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "completed" || status === "failed") {
        return false;
      }
      return 2_000;
    },
  });
}

export function useDeleteObsidianVault() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteObsidianVault,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: obsidianVaultsQueryKey });
    },
  });
}
