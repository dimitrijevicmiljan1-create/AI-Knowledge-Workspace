"use client";

import { useMemo, useState } from "react";

import {
  GitHubConnectPanel,
  RepositoryDiscovery,
  TrackedRepositories,
} from "@/components/github/github-panels";
import { PageHeader } from "@/components/layout/page-header";
import { Skeleton } from "@/components/ui/skeleton";
import { useActiveWorkspace } from "@/hooks/use-active-workspace";
import {
  useAddGitHubRepository,
  useConnectGitHub,
  useDeleteGitHubRepository,
  useDiscoveredRepositories,
  useGitHubConnection,
  useSyncGitHubRepository,
  useTrackedRepositories,
} from "@/hooks/use-github";

export default function GithubPage() {
  const { activeWorkspaceId, isLoading: isWorkspaceLoading } = useActiveWorkspace();
  const connectionQuery = useGitHubConnection();
  const isConnected = Boolean(connectionQuery.data);
  const discoveredQuery = useDiscoveredRepositories(isConnected);
  const trackedQuery = useTrackedRepositories();
  const connectGitHub = useConnectGitHub();
  const addRepository = useAddGitHubRepository();
  const syncRepository = useSyncGitHubRepository();
  const deleteRepository = useDeleteGitHubRepository();
  const [syncingRepositoryId, setSyncingRepositoryId] = useState<string | null>(
    null,
  );

  const trackedRepoIds = useMemo(
    () =>
      new Set(
        (trackedQuery.data ?? []).map((repository) => repository.github_repo_id),
      ),
    [trackedQuery.data],
  );

  if (isWorkspaceLoading) {
    return (
      <section className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-40 w-full" />
      </section>
    );
  }

  if (!activeWorkspaceId) {
    return (
      <section className="space-y-6">
        <PageHeader
          title="GitHub"
          description="Connect repositories to index code and documentation."
        />
        <p className="text-sm text-text-secondary">
          Create a workspace before connecting GitHub repositories.
        </p>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <PageHeader
        title="GitHub"
        description="Connect your GitHub account, add repositories, and sync indexed content."
      />

      <GitHubConnectPanel
        isConnected={isConnected}
        username={connectionQuery.data?.github_username}
        connectedAt={connectionQuery.data?.connected_at}
        isConnecting={connectGitHub.isPending}
        onConnect={() => connectGitHub.mutate()}
        connectionError={connectionQuery.error}
      />

      {isConnected ? (
        <>
          <RepositoryDiscovery
            repositories={discoveredQuery.data?.items ?? []}
            trackedRepoIds={trackedRepoIds}
            isLoading={discoveredQuery.isLoading}
            isAdding={addRepository.isPending}
            error={discoveredQuery.error}
            onAdd={async (repository) => {
              await addRepository.mutateAsync({
                workspace_id: activeWorkspaceId,
                github_repo_id: repository.github_repo_id,
                owner: repository.owner,
                name: repository.name,
              });
            }}
          />

          <TrackedRepositories
            repositories={trackedQuery.data ?? []}
            isLoading={trackedQuery.isLoading}
            syncingRepositoryId={syncingRepositoryId}
            error={trackedQuery.error}
            isRefreshing={trackedQuery.isFetching}
            onRefresh={() => void trackedQuery.refetch()}
            onSync={async (repositoryId) => {
              setSyncingRepositoryId(repositoryId);
              try {
                await syncRepository.mutateAsync(repositoryId);
                await trackedQuery.refetch();
              } finally {
                setSyncingRepositoryId(null);
              }
            }}
            onDelete={async (repositoryId) => {
              await deleteRepository.mutateAsync(repositoryId);
            }}
          />
        </>
      ) : null}
    </section>
  );
}
