import { apiRequest, apiUpload } from "@/lib/api/client";
import type {
  ObsidianSyncJob,
  ObsidianVault,
  ObsidianVaultListResponse,
  ObsidianVaultSyncResponse,
} from "@/lib/api/types";

export type CreateObsidianVaultPayload = {
  workspace_id: string;
  vault_name: string;
};

export async function listObsidianVaults(
  workspaceId: string,
): Promise<ObsidianVaultListResponse> {
  return apiRequest<ObsidianVaultListResponse>(
    `/obsidian/vaults?workspace_id=${workspaceId}`,
  );
}

export async function createObsidianVault(
  payload: CreateObsidianVaultPayload,
): Promise<ObsidianVault> {
  return apiRequest<ObsidianVault>("/obsidian/vaults", {
    method: "POST",
    body: payload,
  });
}

export async function syncObsidianVault(
  vaultId: string,
  files: File[],
): Promise<ObsidianVaultSyncResponse> {
  const formData = new FormData();
  for (const file of files) {
    const relativePath = file.webkitRelativePath || file.name;
    formData.append("files", file, relativePath);
  }
  return apiUpload<ObsidianVaultSyncResponse>(
    `/obsidian/vaults/${vaultId}/sync`,
    formData,
  );
}

export async function getObsidianSyncStatus(
  vaultId: string,
): Promise<ObsidianSyncJob> {
  return apiRequest<ObsidianSyncJob>(`/obsidian/vaults/${vaultId}/status`);
}

export async function deleteObsidianVault(vaultId: string): Promise<void> {
  return apiRequest<void>(`/obsidian/vaults/${vaultId}`, { method: "DELETE" });
}

export type ObsidianDisplaySyncStatus = "synced" | "syncing" | "failed" | "not_synced";

export function mapVaultSyncStatus(status: string): ObsidianDisplaySyncStatus {
  switch (status) {
    case "ready":
      return "synced";
    case "syncing":
      return "syncing";
    case "failed":
      return "failed";
    default:
      return "not_synced";
  }
}

export function extractVaultNameFromFiles(files: File[]): string {
  const firstPath = files[0]?.webkitRelativePath || files[0]?.name || "Vault";
  return firstPath.split("/")[0] || "Vault";
}

export function filterMarkdownFiles(files: File[]): File[] {
  return files.filter((file) => file.name.toLowerCase().endsWith(".md"));
}
