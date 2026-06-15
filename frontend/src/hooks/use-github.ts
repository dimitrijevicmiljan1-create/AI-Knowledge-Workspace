"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  addGitHubRepository,
  connectGitHub,
  deleteGitHubRepository,
  getGitHubConnection,
  getGitHubRepository,
  getGitHubSyncStatus,
  listDiscoveredRepositories,
  syncGitHubRepository,
} from "@/lib/api/github";
import { useUserWorkspace } from "@/hooks/use-user-workspace";
import { hasStoredSession } from "@/lib/auth-storage";
import {
  getStoredRepositories,
  removeStoredRepository,
  upsertStoredRepository,
} from "@/lib/github-storage";
import { isNotFoundError } from "@/lib/errors";

export const githubConnectionQueryKey = ["github", "connection"] as const;
export const githubDiscoveredQueryKey = ["github", "discovered"] as const;
export const githubTrackedQueryKey = ["github", "tracked"] as const;

export function useGitHubConnection() {
  return useQuery({
    queryKey: githubConnectionQueryKey,
    queryFn: async () => {
      try {
        return await getGitHubConnection();
      } catch (error) {
        if (isNotFoundError(error)) {
          return null;
        }
        throw error;
      }
    },
    enabled: hasStoredSession(),
    retry: false,
  });
}

export function useDiscoveredRepositories(enabled = true) {
  return useQuery({
    queryKey: githubDiscoveredQueryKey,
    queryFn: () => listDiscoveredRepositories(),
    enabled: enabled && hasStoredSession(),
  });
}

export function useTrackedRepositories() {
  const { data: workspace } = useUserWorkspace();
  const workspaceId = workspace?.id;

  return useQuery({
    queryKey: [...githubTrackedQueryKey, workspaceId],
    queryFn: async () => {
      const stored = getStoredRepositories(workspaceId!);
      const repositories = await Promise.all(
        stored.map((item) => getGitHubRepository(item.repositoryId)),
      );
      return repositories;
    },
    enabled: hasStoredSession() && Boolean(workspaceId),
    refetchInterval: 10_000,
  });
}

export function useConnectGitHub() {
  return useMutation({
    mutationFn: connectGitHub,
    onSuccess: (data) => {
      window.location.href = data.authorization_url;
    },
  });
}

export function useAddGitHubRepository() {
  const queryClient = useQueryClient();
  const { data: workspace } = useUserWorkspace();

  return useMutation({
    mutationFn: addGitHubRepository,
    onSuccess: (repository) => {
      if (workspace?.id) {
        upsertStoredRepository(workspace.id, {
          repositoryId: repository.id,
          sourceId: repository.source_id,
          githubRepoId: repository.github_repo_id,
          owner: repository.repository_owner,
          name: repository.repository_name,
          defaultBranch: repository.default_branch,
        });
      }
      queryClient.invalidateQueries({ queryKey: githubTrackedQueryKey });
    },
  });
}

export function useSyncGitHubRepository() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: syncGitHubRepository,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: githubTrackedQueryKey });
    },
  });
}

export function useGitHubSyncStatus(repositoryId: string | null, enabled = false) {
  return useQuery({
    queryKey: ["github", "sync-status", repositoryId],
    queryFn: () => getGitHubSyncStatus(repositoryId!),
    enabled: enabled && Boolean(repositoryId) && hasStoredSession(),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "completed" || status === "failed") {
        return false;
      }
      return 2_000;
    },
  });
}

export function useDeleteGitHubRepository() {
  const queryClient = useQueryClient();
  const { data: workspace } = useUserWorkspace();

  return useMutation({
    mutationFn: deleteGitHubRepository,
    onSuccess: (_data, repositoryId) => {
      if (workspace?.id) {
        removeStoredRepository(workspace.id, repositoryId);
      }
      queryClient.invalidateQueries({ queryKey: githubTrackedQueryKey });
    },
  });
}
