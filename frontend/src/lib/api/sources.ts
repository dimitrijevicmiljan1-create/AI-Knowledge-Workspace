import { apiRequest, apiUpload } from "@/lib/api/client";
import type {
  DocumentStats,
  FileUploadResponse,
  MultipleFileUploadResponse,
  SourceListResponse,
  SourceStats,
  WorkspaceFileListResponse,
} from "@/lib/api/types";

const ALLOWED_EXTENSIONS = [".txt", ".md", ".pdf", ".docx"] as const;

export function isAllowedUploadFile(file: File): boolean {
  const name = file.name.toLowerCase();
  return ALLOWED_EXTENSIONS.some((ext) => name.endsWith(ext));
}

export async function listUploads(
  workspaceId: string,
): Promise<WorkspaceFileListResponse> {
  return apiRequest<WorkspaceFileListResponse>(
    `/uploads?workspace_id=${workspaceId}`,
  );
}

export async function uploadFile(
  workspaceId: string,
  file: File,
): Promise<FileUploadResponse> {
  const formData = new FormData();
  formData.append("workspace_id", workspaceId);
  formData.append("file", file);
  return apiUpload<FileUploadResponse>("/uploads", formData);
}

export async function uploadMultipleFiles(
  workspaceId: string,
  files: File[],
): Promise<MultipleFileUploadResponse> {
  const formData = new FormData();
  formData.append("workspace_id", workspaceId);
  for (const file of files) {
    formData.append("files", file);
  }
  return apiUpload<MultipleFileUploadResponse>("/uploads/multiple", formData);
}

export async function deleteUpload(documentId: string): Promise<void> {
  return apiRequest<void>(`/uploads/${documentId}`, { method: "DELETE" });
}

export async function getDocumentStats(
  documentId: string,
): Promise<DocumentStats> {
  return apiRequest<DocumentStats>(`/documents/${documentId}/stats`);
}

export async function listSources(
  workspaceId: string,
): Promise<SourceListResponse> {
  return apiRequest<SourceListResponse>(
    `/sources?workspace_id=${workspaceId}`,
  );
}

export async function getSourceStats(sourceId: string): Promise<SourceStats> {
  return apiRequest<SourceStats>(`/sources/${sourceId}/stats`);
}

export type DocumentDisplayStatus =
  | "uploading"
  | "processing"
  | "indexed"
  | "failed";

export function mapDocumentStatus(
  stats: DocumentStats | undefined,
  uploadFailed = false,
): DocumentDisplayStatus {
  if (uploadFailed) {
    return "failed";
  }
  if (!stats) {
    return "processing";
  }
  if (stats.chunk_count > 0 && stats.indexed_at) {
    return "indexed";
  }
  return "processing";
}
