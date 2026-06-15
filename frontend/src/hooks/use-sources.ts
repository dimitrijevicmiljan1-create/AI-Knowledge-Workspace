"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  deleteUpload,
  getDocumentStats,
  listUploads,
  uploadFile,
  uploadMultipleFiles,
} from "@/lib/api/sources";
import { useUserWorkspace } from "@/hooks/use-user-workspace";
import { hasStoredSession } from "@/lib/auth-storage";

export const uploadsQueryKey = ["uploads"] as const;
export const documentStatsQueryKey = ["document-stats"] as const;

export function useUploads() {
  const { data: workspace } = useUserWorkspace();
  const workspaceId = workspace?.id;

  return useQuery({
    queryKey: [...uploadsQueryKey, workspaceId],
    queryFn: () => listUploads(workspaceId!),
    enabled: hasStoredSession() && Boolean(workspaceId),
    refetchInterval: 10_000,
  });
}

export function useDocumentStats(documentIds: string[]) {
  return useQuery({
    queryKey: [...documentStatsQueryKey, documentIds],
    queryFn: async () => {
      const results = await Promise.all(
        documentIds.map(async (documentId) => ({
          documentId,
          stats: await getDocumentStats(documentId),
        })),
      );
      return Object.fromEntries(
        results.map(({ documentId, stats }) => [documentId, stats]),
      );
    },
    enabled: hasStoredSession() && documentIds.length > 0,
    refetchInterval: 5_000,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  const { data: workspace } = useUserWorkspace();

  return useMutation({
    mutationFn: async (file: File) => {
      if (!workspace?.id) {
        throw new Error("Workspace is not ready");
      }
      return uploadFile(workspace.id, file);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: uploadsQueryKey });
      queryClient.invalidateQueries({ queryKey: documentStatsQueryKey });
    },
  });
}

export function useUploadDocuments() {
  const queryClient = useQueryClient();
  const { data: workspace } = useUserWorkspace();

  return useMutation({
    mutationFn: async (files: File[]) => {
      if (!workspace?.id) {
        throw new Error("Workspace is not ready");
      }
      if (files.length === 1) {
        const response = await uploadFile(workspace.id, files[0]);
        return {
          uploaded: response.file.status === "created" ? 1 : 0,
          skipped: response.file.status === "skipped" ? 1 : 0,
          failed: response.file.status === "failed" ? 1 : 0,
          results: [response.file],
        };
      }
      return uploadMultipleFiles(workspace.id, files);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: uploadsQueryKey });
      queryClient.invalidateQueries({ queryKey: documentStatsQueryKey });
    },
  });
}

export function useDeleteUpload() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: string) => deleteUpload(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: uploadsQueryKey });
      queryClient.invalidateQueries({ queryKey: documentStatsQueryKey });
    },
  });
}
