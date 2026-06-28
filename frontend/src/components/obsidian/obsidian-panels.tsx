"use client";

import { Loader2, RefreshCw, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";

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
  mapVaultSyncStatus,
  type ObsidianDisplaySyncStatus,
} from "@/lib/api/obsidian";
import type { ObsidianVault } from "@/lib/api/types";
import { getErrorMessage } from "@/lib/errors";

type TrackedVaultsProps = {
  vaults: ObsidianVault[];
  isLoading: boolean;
  onDelete: (vaultId: string) => Promise<void>;
  onRefresh: () => void;
  isRefreshing: boolean;
  error?: unknown;
};

function syncStatusConfig(status: ObsidianDisplaySyncStatus): {
  label: string;
  variant: "default" | "success" | "warning" | "danger" | "info";
} {
  switch (status) {
    case "synced":
      return { label: "Indexed", variant: "success" };
    case "syncing":
      return { label: "Scanning", variant: "info" };
    case "failed":
      return { label: "Failed", variant: "danger" };
    case "not_synced":
      return { label: "Not synced", variant: "warning" };
  }
}

export function TrackedVaults({
  vaults,
  isLoading,
  onDelete,
  onRefresh,
  isRefreshing,
  error,
}: TrackedVaultsProps) {
  const [actionError, setActionError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const sortedVaults = useMemo(
    () =>
      [...vaults].sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      ),
    [vaults],
  );

  if (isLoading) {
    return <Skeleton className="h-48 w-full" />;
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <CardTitle>Connected vaults</CardTitle>
          <CardDescription>
            Obsidian vaults indexed in your workspace.
          </CardDescription>
        </div>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          onClick={onRefresh}
          disabled={isRefreshing}
        >
          <RefreshCw className={isRefreshing ? "size-4 animate-spin" : "size-4"} />
          Refresh
        </Button>
      </CardHeader>
      <CardContent className="space-y-3">
        {error ? (
          <ErrorBanner
            message={getErrorMessage(error, "Unable to load Obsidian vaults.")}
          />
        ) : null}
        {actionError ? <ErrorBanner message={actionError} /> : null}

        {sortedVaults.length === 0 ? (
          <p className="text-sm text-text-secondary">
            No vaults connected yet. Choose a vault folder above to get started.
          </p>
        ) : (
          sortedVaults.map((vault) => {
            const displayStatus = mapVaultSyncStatus(vault.sync_status);
            const config = syncStatusConfig(displayStatus);

            return (
              <div
                key={vault.id}
                className="flex flex-col gap-3 rounded-xl border border-border bg-surface p-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{vault.vault_name}</p>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-meta">
                    <StatusBadge label={config.label} variant={config.variant} />
                    {vault.last_synced_at ? (
                      <span>
                        Last synced{" "}
                        {new Date(vault.last_synced_at).toLocaleString()}
                      </span>
                    ) : null}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    disabled={deletingId === vault.id}
                    onClick={async () => {
                      setActionError(null);
                      setDeletingId(vault.id);
                      try {
                        await onDelete(vault.id);
                      } catch (deleteError) {
                        setActionError(
                          getErrorMessage(deleteError, "Unable to remove vault."),
                        );
                      } finally {
                        setDeletingId(null);
                      }
                    }}
                  >
                    {deletingId === vault.id ? (
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
