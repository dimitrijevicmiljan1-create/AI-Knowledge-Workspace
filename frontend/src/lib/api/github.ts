import { apiRequest } from "@/lib/api/client";
import type {
  GitHubConnectResponse,
  GitHubConnection,
  GitHubRepository,
  GitHubRepositoryDiscoveryResponse,
  GitHubRepositorySyncResponse,
  GitHubSyncJob,
} from "@/lib/api/types";

export async function connectGitHub(): Promise<GitHubConnectResponse> {
  return apiRequest<GitHubConnectResponse>("/github/connect", {
    method: "POST",
  });
}

export async function getGitHubConnection(): Promise<GitHubConnection> {
  return apiRequest<GitHubConnection>("/github/connection");
}

export async function listDiscoveredRepositories(
  page = 1,
  perPage = 100,
): Promise<GitHubRepositoryDiscoveryResponse> {
  return apiRequest<GitHubRepositoryDiscoveryResponse>(
    `/github/repositories?page=${page}&per_page=${perPage}`,
  );
}

export type AddGitHubRepositoryPayload = {
  workspace_id: string;
  github_repo_id: number;
  owner: string;
  name: string;
};

export async function addGitHubRepository(
  payload: AddGitHubRepositoryPayload,
): Promise<GitHubRepository> {
  return apiRequest<GitHubRepository>("/github/repositories", {
    method: "POST",
    body: payload,
  });
}

export async function getGitHubRepository(
  repositoryId: string,
): Promise<GitHubRepository> {
  return apiRequest<GitHubRepository>(`/github/repositories/${repositoryId}`);
}

export async function syncGitHubRepository(
  repositoryId: string,
): Promise<GitHubRepositorySyncResponse> {
  return apiRequest<GitHubRepositorySyncResponse>(
    `/github/repositories/${repositoryId}/sync`,
    { method: "POST" },
  );
}

export async function getGitHubSyncStatus(
  repositoryId: string,
): Promise<GitHubSyncJob> {
  return apiRequest<GitHubSyncJob>(
    `/github/repositories/${repositoryId}/status`,
  );
}

export async function deleteGitHubRepository(
  repositoryId: string,
): Promise<void> {
  return apiRequest<void>(`/github/repositories/${repositoryId}`, {
    method: "DELETE",
  });
}

export type GitHubDisplaySyncStatus =
  | "synced"
  | "syncing"
  | "failed"
  | "not_synced";

export function mapRepositorySyncStatus(
  syncStatus: GitHubRepository["sync_status"],
  jobStatus?: GitHubSyncJob["status"],
): GitHubDisplaySyncStatus {
  if (jobStatus === "processing" || jobStatus === "pending") {
    return "syncing";
  }
  if (jobStatus === "failed" || syncStatus === "failed") {
    return "failed";
  }
  if (syncStatus === "ready") {
    return "synced";
  }
  if (syncStatus === "syncing") {
    return "syncing";
  }
  return "not_synced";
}
