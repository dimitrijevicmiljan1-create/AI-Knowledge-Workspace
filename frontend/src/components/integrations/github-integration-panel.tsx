"use client";

import { useMemo, useState } from "react";
import { FolderGit2 } from "lucide-react";

import {
  GitHubConnectPanel,
  RepositoryDiscovery,
  TrackedRepositories,
} from "@/components/github/github-panels";
import { IntegrationCard } from "@/components/integrations/integration-card";
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

type GitHubIntegrationPanelProps = {
  isExpanded: boolean;
  onToggle: () => void;
};

export function GitHubIntegrationPanel({
  isExpanded,
  onToggle,
}: GitHubIntegrationPanelProps) {
  const { data: workspace } = useUserWorkspace();
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

  const lastSyncedAt = useMemo(() => {
    const timestamps = (trackedQuery.data ?? [])
      .map((repository) => repository.last_synced_at)
      .filter(Boolean)
      .map((value) => new Date(value as string).getTime());
    if (timestamps.length === 0) {
      return null;
    }
    return new Date(Math.max(...timestamps)).toLocaleString();
  }, [trackedQuery.data]);

  const repositoryCount = trackedQuery.data?.length ?? 0;

  return (
    <>
      <IntegrationCard
        name="GitHub"
        description="Connect repositories and sync code, docs, and markdown into your workspace."
        icon={FolderGit2}
        status={isConnected ? "connected" : "disconnected"}
        stats={
          isConnected
            ? [
                {
                  label: "Repositories",
                  value: String(repositoryCount),
                },
                {
                  label: "Last sync",
                  value: lastSyncedAt ?? "Not synced yet",
                },
              ]
            : undefined
        }
        connectLabel="Connect GitHub"
        onConnect={() => connectGitHub.mutate()}
        isConnecting={connectGitHub.isPending}
        manageLabel={isExpanded ? "Hide details" : "Manage"}
        onManage={isConnected ? onToggle : undefined}
        isExpanded={isExpanded}
      />

      {isConnected && isExpanded ? (
        <div className="col-span-full space-y-4">
          <GitHubConnectPanel
            isConnected={isConnected}
            username={connectionQuery.data?.github_username}
            connectedAt={connectionQuery.data?.connected_at}
            isConnecting={connectGitHub.isPending}
            onConnect={() => connectGitHub.mutate()}
            connectionError={connectionQuery.error}
          />

          {workspace ? (
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
        </div>
      ) : null}
    </>
  );
}
