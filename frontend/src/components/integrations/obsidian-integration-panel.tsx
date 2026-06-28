"use client";

import { useEffect, useMemo, useState } from "react";
import { BookMarked } from "lucide-react";

import { IntegrationCard } from "@/components/integrations/integration-card";
import { TrackedVaults } from "@/components/obsidian/obsidian-panels";
import { VaultFolderPicker } from "@/components/obsidian/vault-folder-picker";
import { ErrorBanner } from "@/components/ui/error-banner";
import {
  useCreateObsidianVault,
  useDeleteObsidianVault,
  useObsidianSyncStatus,
  useObsidianVaults,
  useSyncObsidianVault,
} from "@/hooks/use-obsidian";
import { useUserWorkspace } from "@/hooks/use-user-workspace";
import { extractVaultNameFromFiles } from "@/lib/api/obsidian";
import { getErrorMessage } from "@/lib/errors";

type ObsidianIntegrationPanelProps = {
  isExpanded: boolean;
  onToggle: () => void;
};

export function ObsidianIntegrationPanel({
  isExpanded,
  onToggle,
}: ObsidianIntegrationPanelProps) {
  const { data: workspace } = useUserWorkspace();
  const vaultsQuery = useObsidianVaults();
  const createVault = useCreateObsidianVault();
  const syncVault = useSyncObsidianVault();
  const deleteVault = useDeleteObsidianVault();
  const [syncingVaultId, setSyncingVaultId] = useState<string | null>(null);
  const [activeSyncVaultId, setActiveSyncVaultId] = useState<string | null>(null);
  const [connectError, setConnectError] = useState<string | null>(null);
  const [indexedSummary, setIndexedSummary] = useState<string | null>(null);

  const syncStatusQuery = useObsidianSyncStatus(
    activeSyncVaultId,
    Boolean(activeSyncVaultId),
  );

  const vaults = useMemo(
    () => vaultsQuery.data?.items ?? [],
    [vaultsQuery.data?.items],
  );
  const isConnected = vaults.length > 0;

  const lastSyncedAt = useMemo(() => {
    const timestamps = vaults
      .map((vault) => vault.last_synced_at)
      .filter(Boolean)
      .map((value) => new Date(value as string).getTime());
    if (timestamps.length === 0) {
      return null;
    }
    return new Date(Math.max(...timestamps)).toLocaleString();
  }, [vaults]);

  useEffect(() => {
    const job = syncStatusQuery.data;
    if (!job || !activeSyncVaultId) {
      return;
    }

    if (job.status === "completed") {
      const total = job.documents_created + job.documents_updated;
      setIndexedSummary(`Indexed ${total} notes`);
      setSyncingVaultId(null);
      setActiveSyncVaultId(null);
      void vaultsQuery.refetch();
    }

    if (job.status === "failed") {
      setConnectError(job.error_message ?? "Vault indexing failed.");
      setSyncingVaultId(null);
      setActiveSyncVaultId(null);
    }
  }, [activeSyncVaultId, syncStatusQuery.data, vaultsQuery]);

  async function handleConnectVault(files: File[]) {
    if (!workspace) {
      return;
    }

    setConnectError(null);
    setIndexedSummary(null);
    const vaultName = extractVaultNameFromFiles(files);

    try {
      const vault = await createVault.mutateAsync({
        workspace_id: workspace.id,
        vault_name: vaultName,
      });
      setSyncingVaultId(vault.id);
      const syncResponse = await syncVault.mutateAsync({ vaultId: vault.id, files });
      setActiveSyncVaultId(syncResponse.vault_id);
    } catch (error) {
      setConnectError(getErrorMessage(error, "Unable to connect Obsidian vault."));
      setSyncingVaultId(null);
      setActiveSyncVaultId(null);
    }
  }

  const isBusy =
    createVault.isPending ||
    syncVault.isPending ||
    syncingVaultId !== null ||
    syncStatusQuery.isFetching;

  return (
    <>
      <IntegrationCard
        name="Obsidian"
        description="Sync notes and markdown files from your Obsidian vault."
        icon={BookMarked}
        status={isConnected ? "connected" : "disconnected"}
        stats={
          isConnected
            ? [
                {
                  label: "Vaults",
                  value: String(vaults.length),
                },
                {
                  label: "Last sync",
                  value: lastSyncedAt ?? "Not synced yet",
                },
              ]
            : undefined
        }
        connectLabel="Connect vault"
        onConnect={onToggle}
        manageLabel={isExpanded ? "Hide details" : "Manage"}
        onManage={isConnected || isExpanded ? onToggle : undefined}
        isExpanded={isExpanded}
      />

      {isExpanded ? (
        <div className="col-span-full space-y-4">
          {connectError ? <ErrorBanner message={connectError} /> : null}
          {indexedSummary ? (
            <p className="rounded-xl border border-success/30 bg-success/10 px-3 py-2 text-sm text-success">
              {indexedSummary}
            </p>
          ) : null}

          <VaultFolderPicker
            onSelect={handleConnectVault}
            isLoading={isBusy}
            disabled={!workspace}
          />

          <TrackedVaults
            vaults={vaults}
            isLoading={vaultsQuery.isLoading}
            onDelete={async (vaultId) => {
              await deleteVault.mutateAsync(vaultId);
            }}
            onRefresh={() => void vaultsQuery.refetch()}
            isRefreshing={vaultsQuery.isFetching}
            error={vaultsQuery.error}
          />
        </div>
      ) : null}
    </>
  );
}
