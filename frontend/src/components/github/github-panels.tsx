"use client";

import {
  FolderGit2,
  GitBranch,
  Loader2,
  RefreshCw,
  Trash2,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { ErrorBanner } from "@/components/ui/error-banner";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/ui/status-badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  mapRepositorySyncStatus,
  type GitHubDisplaySyncStatus,
} from "@/lib/api/github";
import type { GitHubDiscoveredRepository, GitHubRepository } from "@/lib/api/types";
import { getErrorMessage, isNotFoundError } from "@/lib/errors";

type GitHubConnectPanelProps = {
  isConnected: boolean;
  username?: string;
  connectedAt?: string;
  isConnecting: boolean;
  onConnect: () => void;
  connectionError?: unknown;
};

export function GitHubConnectPanel({
  isConnected,
  username,
  connectedAt,
  isConnecting,
  onConnect,
  connectionError,
}: GitHubConnectPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>GitHub connection</CardTitle>
        <CardDescription>
          Connect your GitHub account to discover and sync repositories.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {connectionError && !isNotFoundError(connectionError) ? (
          <ErrorBanner
            message={getErrorMessage(
              connectionError,
              "Unable to verify GitHub connection.",
            )}
          />
        ) : null}

        {isConnected && username ? (
          <div className="flex flex-col gap-3 rounded-xl border border-border bg-surface p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium">Connected as @{username}</p>
              {connectedAt ? (
                <p className="text-meta">
                  Connected {new Date(connectedAt).toLocaleString()}
                </p>
              ) : null}
            </div>
            <StatusBadge label="Connected" variant="success" />
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-text-secondary">
              Authorize this app through GitHub OAuth to browse your repositories.
            </p>
            <Button
              type="button"
              onClick={onConnect}
              disabled={isConnecting}
            >
              {isConnecting ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <FolderGit2 className="size-4" />
              )}
              Connect GitHub
            </Button>
            <p className="text-meta">
              After authorization, GitHub redirects to the API callback URL. Return
              to this page to continue.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

type RepositoryDiscoveryProps = {
  repositories: GitHubDiscoveredRepository[];
  trackedRepoIds: Set<number>;
  isLoading: boolean;
  isAdding: boolean;
  onAdd: (repository: GitHubDiscoveredRepository) => Promise<void>;
  error?: unknown;
};

export function RepositoryDiscovery({
  repositories,
  trackedRepoIds,
  isLoading,
  isAdding,
  onAdd,
  error,
}: RepositoryDiscoveryProps) {
  const [actionError, setActionError] = useState<string | null>(null);

  if (isLoading) {
    return <Skeleton className="h-48 w-full" />;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Discover repositories</CardTitle>
        <CardDescription>
          Select repositories from your GitHub account to add to this workspace.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {error ? (
          <ErrorBanner
            message={getErrorMessage(error, "Unable to load repositories.")}
          />
        ) : null}
        {actionError ? <ErrorBanner message={actionError} /> : null}

        {repositories.length === 0 ? (
          <p className="text-sm text-text-secondary">
            No repositories found. Connect GitHub to browse your repositories.
          </p>
        ) : (
          <div className="space-y-2">
            {repositories.map((repository) => {
              const isTracked = trackedRepoIds.has(repository.github_repo_id);
              return (
                <div
                  key={repository.github_repo_id}
                  className="flex flex-col gap-3 rounded-xl border border-border bg-surface p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">
                      {repository.full_name}
                    </p>
                    <div className="mt-1 flex flex-wrap items-center gap-2 text-meta">
                      <span className="inline-flex items-center gap-1">
                        <GitBranch className="size-3" />
                        {repository.default_branch}
                      </span>
                      <span>{repository.owner}</span>
                      {repository.private ? (
                        <StatusBadge label="Private" variant="default" />
                      ) : (
                        <StatusBadge label="Public" variant="info" />
                      )}
                    </div>
                  </div>
                  <Button
                    type="button"
                    size="sm"
                    variant={isTracked ? "secondary" : "default"}
                    disabled={isTracked || isAdding}
                    onClick={async () => {
                      setActionError(null);
                      try {
                        await onAdd(repository);
                      } catch (addError) {
                        setActionError(
                          getErrorMessage(addError, "Unable to add repository."),
                        );
                      }
                    }}
                  >
                    {isTracked ? "Added" : "Add to workspace"}
                  </Button>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function syncStatusConfig(status: GitHubDisplaySyncStatus): {
  label: string;
  variant: "default" | "success" | "warning" | "danger" | "info";
} {
  switch (status) {
    case "synced":
      return { label: "Synced", variant: "success" };
    case "syncing":
      return { label: "Syncing", variant: "info" };
    case "failed":
      return { label: "Failed", variant: "danger" };
    case "not_synced":
      return { label: "Not synced", variant: "warning" };
  }
}

type TrackedRepositoriesProps = {
  repositories: GitHubRepository[];
  isLoading: boolean;
  syncingRepositoryId: string | null;
  onSync: (repositoryId: string) => Promise<void>;
  onDelete: (repositoryId: string) => Promise<void>;
  onRefresh: () => void;
  isRefreshing: boolean;
  error?: unknown;
};

export function TrackedRepositories({
  repositories,
  isLoading,
  syncingRepositoryId,
  onSync,
  onDelete,
  onRefresh,
  isRefreshing,
  error,
}: TrackedRepositoriesProps) {
  const [actionError, setActionError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const sortedRepositories = useMemo(
    () =>
      [...repositories].sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      ),
    [repositories],
  );

  if (isLoading) {
    return <Skeleton className="h-48 w-full" />;
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <CardTitle>Tracked repositories</CardTitle>
          <CardDescription>
            Repositories indexed in your active workspace.
          </CardDescription>
        </div>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          onClick={onRefresh}
          disabled={isRefreshing}
        >
          <RefreshCw
            className={isRefreshing ? "size-4 animate-spin" : "size-4"}
          />
          Refresh
        </Button>
      </CardHeader>
      <CardContent className="space-y-3">
        {error ? (
          <ErrorBanner
            message={getErrorMessage(error, "Unable to load tracked repositories.")}
          />
        ) : null}
        {actionError ? <ErrorBanner message={actionError} /> : null}

        {sortedRepositories.length === 0 ? (
          <p className="text-sm text-text-secondary">
            No tracked repositories yet. Add a repository from the discovery list
            above.
          </p>
        ) : (
          sortedRepositories.map((repository) => {
            const displayStatus = mapRepositorySyncStatus(repository.sync_status);
            const config = syncStatusConfig(displayStatus);
            const isSyncing = syncingRepositoryId === repository.id;

            return (
              <div
                key={repository.id}
                className="flex flex-col gap-3 rounded-xl border border-border bg-surface p-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">
                    {repository.repository_owner}/{repository.repository_name}
                  </p>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-meta">
                    <StatusBadge label={config.label} variant={config.variant} />
                    <span className="inline-flex items-center gap-1">
                      <GitBranch className="size-3" />
                      {repository.default_branch}
                    </span>
                    {repository.last_synced_at ? (
                      <span>
                        Last synced{" "}
                        {new Date(repository.last_synced_at).toLocaleString()}
                      </span>
                    ) : null}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    size="sm"
                    variant="secondary"
                    disabled={isSyncing}
                    onClick={async () => {
                      setActionError(null);
                      try {
                        await onSync(repository.id);
                      } catch (syncError) {
                        setActionError(
                          getErrorMessage(syncError, "Unable to start sync."),
                        );
                      }
                    }}
                  >
                    {isSyncing ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <RefreshCw className="size-4" />
                    )}
                    Sync
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    disabled={deletingId === repository.id}
                    onClick={async () => {
                      setActionError(null);
                      setDeletingId(repository.id);
                      try {
                        await onDelete(repository.id);
                      } catch (deleteError) {
                        setActionError(
                          getErrorMessage(deleteError, "Unable to remove repository."),
                        );
                      } finally {
                        setDeletingId(null);
                      }
                    }}
                  >
                    {deletingId === repository.id ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <Trash2 className="size-4" />
                    )}
                    Remove
                  </Button>
                </div>
              </div>
            );
          })
        )}
      </CardContent>
    </Card>
  );
}

export function GitHubSyncPoller({
  repositoryId,
  enabled,
  onComplete,
}: {
  repositoryId: string;
  enabled: boolean;
  onComplete: () => void;
}) {
  const [pollCount, setPollCount] = useState(0);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    let cancelled = false;
    const interval = setInterval(async () => {
      if (cancelled) {
        return;
      }
      try {
        const { getGitHubSyncStatus } = await import("@/lib/api/github");
        const status = await getGitHubSyncStatus(repositoryId);
        setPollCount((count) => count + 1);
        if (status.status === "completed" || status.status === "failed") {
          onComplete();
          clearInterval(interval);
        }
      } catch {
        if (pollCount > 10) {
          clearInterval(interval);
        }
      }
    }, 2000);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [enabled, onComplete, pollCount, repositoryId]);

  return null;
}
