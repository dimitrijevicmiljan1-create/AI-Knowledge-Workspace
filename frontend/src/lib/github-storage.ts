export type StoredGitHubRepository = {
  repositoryId: string;
  sourceId: string;
  githubRepoId: number;
  owner: string;
  name: string;
  defaultBranch: string;
};

function storageKey(workspaceId: string): string {
  return `github_repos_${workspaceId}`;
}

export function getStoredRepositories(
  workspaceId: string,
): StoredGitHubRepository[] {
  if (typeof window === "undefined") {
    return [];
  }
  const raw = localStorage.getItem(storageKey(workspaceId));
  if (!raw) {
    return [];
  }
  try {
    return JSON.parse(raw) as StoredGitHubRepository[];
  } catch {
    return [];
  }
}

export function upsertStoredRepository(
  workspaceId: string,
  repository: StoredGitHubRepository,
): void {
  const existing = getStoredRepositories(workspaceId);
  const index = existing.findIndex(
    (item) =>
      item.repositoryId === repository.repositoryId ||
      item.githubRepoId === repository.githubRepoId,
  );
  if (index >= 0) {
    existing[index] = repository;
  } else {
    existing.push(repository);
  }
  localStorage.setItem(storageKey(workspaceId), JSON.stringify(existing));
}

export function removeStoredRepository(
  workspaceId: string,
  repositoryId: string,
): void {
  const filtered = getStoredRepositories(workspaceId).filter(
    (item) => item.repositoryId !== repositoryId,
  );
  localStorage.setItem(storageKey(workspaceId), JSON.stringify(filtered));
}
