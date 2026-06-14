const ACTIVE_WORKSPACE_KEY = "active_workspace_id";

export function getActiveWorkspaceId(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem(ACTIVE_WORKSPACE_KEY);
}

export function setActiveWorkspaceId(workspaceId: string): void {
  localStorage.setItem(ACTIVE_WORKSPACE_KEY, workspaceId);
}

export function clearActiveWorkspaceId(): void {
  localStorage.removeItem(ACTIVE_WORKSPACE_KEY);
}
