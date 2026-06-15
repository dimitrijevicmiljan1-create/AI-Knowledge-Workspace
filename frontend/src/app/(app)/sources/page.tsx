"use client";

import {
  GitHubConnectPanel,
  RepositoryDiscovery,
  TrackedRepositories,
} from "@/components/github/github-panels";
import { ObsidianComingSoon } from "@/components/obsidian/obsidian-coming-soon";
import { PageHeader } from "@/components/layout/page-header";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useAddGitHubRepository,
  useConnectGitHub,
  useDeleteGitHubRepository,
  useDiscoveredRepositories,
  useGitHubConnection,
  useSyncGitHubRepository,
  useTrackedRepositories,
} from "@/hooks/use-github";
import { useUserWorkspace } from "@/hooks/use-user-workspace";
import { useMemo, useState } from "react";

export default function SourcesPage() {
  const { data: workspace, isLoading: isWorkspaceLoading } = useUserWorkspace();
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

  return (
    <section className="space-y-6">
      <PageHeader
        title="Sources"
        description="Connect external knowledge sources to your personal workspace."
      />

      <GitHubConnectPanel
        isConnected={isConnected}
        username={connectionQuery.data?.github_username}
        connectedAt={connectionQuery.data?.connected_at}
        isConnecting={connectGitHub.isPending}
        onConnect={() => connectGitHub.mutate()}
        connectionError={connectionQuery.error}
      />

      {isConnected && workspace ? (
        <>
          <RepositoryDiscovery
            repositories={discoveredQuery.data?.items ?? []}
            trackedRepoIds={trackedRepoIds}
            isLoading={discoveredQuery.isLoading}
            isAdding={addRepository.isPending}
            error={discoveredQuery.error}
            onAdd={async (repository) => {
              await addRepository.mutateAsync({
                workspace_id: workspace.id,
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

      <ObsidianComingSoon />
    </section>
  );
}
