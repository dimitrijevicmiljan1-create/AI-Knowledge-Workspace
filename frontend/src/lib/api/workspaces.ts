import { apiRequest } from "@/lib/api/client";
import type {
  WorkspaceListResponse,
  WorkspaceStats,
} from "@/lib/api/types";

export async function listWorkspaces(): Promise<WorkspaceListResponse> {
  return apiRequest<WorkspaceListResponse>("/workspaces");
}

export async function getWorkspaceStats(
  workspaceId: string,
): Promise<WorkspaceStats> {
  return apiRequest<WorkspaceStats>(`/workspaces/${workspaceId}/stats`);
}

export type DashboardSummary = {
  workspaceCount: number;
  documentCount: number;
  conversationCount: number;
};

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const { items } = await listWorkspaces();

  if (items.length === 0) {
    return {
      workspaceCount: 0,
      documentCount: 0,
      conversationCount: 0,
    };
  }

  const stats = await Promise.all(
    items.map((workspace) => getWorkspaceStats(workspace.id)),
  );

  return {
    workspaceCount: items.length,
    documentCount: stats.reduce((sum, item) => sum + item.document_count, 0),
    conversationCount: stats.reduce((sum, item) => sum + item.chat_count, 0),
  };
}
