"use client";

import {
  Eye,
  Loader2,
  RefreshCw,
  Trash2,
} from "lucide-react";
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
  mapDocumentStatus,
  type DocumentDisplayStatus,
} from "@/lib/api/sources";
import type { DocumentStats, WorkspaceFile } from "@/lib/api/types";
import { getErrorMessage } from "@/lib/errors";

type DocumentsListProps = {
  files: WorkspaceFile[];
  statsByDocumentId: Record<string, DocumentStats | undefined>;
  isLoading: boolean;
  isRefreshing: boolean;
  onRefresh: () => void;
  onDelete: (documentId: string) => Promise<void>;
  error?: unknown;
};

function statusConfig(status: DocumentDisplayStatus): {
  label: string;
  variant: "default" | "success" | "warning" | "danger" | "info";
} {
  switch (status) {
    case "uploading":
      return { label: "Uploading", variant: "info" };
    case "processing":
      return { label: "Processing", variant: "warning" };
    case "indexed":
      return { label: "Indexed", variant: "success" };
    case "failed":
      return { label: "Failed", variant: "danger" };
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function DocumentsList({
  files,
  statsByDocumentId,
  isLoading,
  isRefreshing,
  onRefresh,
  onDelete,
  error,
}: DocumentsListProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<WorkspaceFile | null>(
    null,
  );
  const [actionError, setActionError] = useState<string | null>(null);

  const sortedFiles = useMemo(
    () =>
      [...files].sort(
        (a, b) =>
          new Date(b.uploaded_at).getTime() - new Date(a.uploaded_at).getTime(),
      ),
    [files],
  );

  async function handleDelete(documentId: string) {
    setActionError(null);
    setDeletingId(documentId);
    try {
      await onDelete(documentId);
      if (selectedDocument?.document_id === documentId) {
        setSelectedDocument(null);
      }
    } catch (deleteError) {
      setActionError(getErrorMessage(deleteError, "Unable to delete document."));
    } finally {
      setDeletingId(null);
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-4 w-64" />
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <CardTitle>Documents</CardTitle>
          <CardDescription>
            Uploaded files in your active workspace.
          </CardDescription>
        </div>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          onClick={onRefresh}
          disabled={isRefreshing}
          aria-label="Refresh documents"
        >
          <RefreshCw
            className={isRefreshing ? "size-4 animate-spin" : "size-4"}
          />
          Refresh
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {error ? (
          <ErrorBanner
            message={getErrorMessage(error, "Unable to load documents.")}
          />
        ) : null}
        {actionError ? <ErrorBanner message={actionError} /> : null}

        {sortedFiles.length === 0 ? (
          <p className="text-sm text-text-secondary">
            No documents uploaded yet. Upload files above to get started.
          </p>
        ) : (
          <div className="space-y-3">
            {sortedFiles.map((file) => {
              const stats = statsByDocumentId[file.document_id];
              const status = mapDocumentStatus(stats);
              const config = statusConfig(status);

              return (
                <div
                  key={file.document_id}
                  className="flex flex-col gap-3 rounded-xl border border-border bg-surface p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="min-w-0 space-y-1">
                    <p className="truncate text-sm font-medium">{file.filename}</p>
                    <div className="flex flex-wrap items-center gap-2 text-meta">
                      <StatusBadge label={config.label} variant={config.variant} />
                      <span>{formatFileSize(file.size)}</span>
                      <span>
                        {new Date(file.uploaded_at).toLocaleString()}
                      </span>
                      {stats?.chunk_count ? (
                        <span>{stats.chunk_count} chunks</span>
                      ) : null}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedDocument(file)}
                      aria-label={`View ${file.filename}`}
                    >
                      <Eye className="size-4" />
                      View
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      disabled={deletingId === file.document_id}
                      onClick={() => void handleDelete(file.document_id)}
                      aria-label={`Delete ${file.filename}`}
                    >
                      {deletingId === file.document_id ? (
                        <Loader2 className="size-4 animate-spin" />
                      ) : (
                        <Trash2 className="size-4" />
                      )}
                      Delete
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {selectedDocument ? (
          <div className="rounded-xl border border-border bg-elevated p-4">
            <div className="mb-2 flex items-center justify-between gap-2">
              <h3 className="text-sm font-semibold">{selectedDocument.filename}</h3>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => setSelectedDocument(null)}
              >
                Close
              </Button>
            </div>
            <dl className="grid gap-2 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-meta">Document ID</dt>
                <dd className="break-all">{selectedDocument.document_id}</dd>
              </div>
              <div>
                <dt className="text-meta">Uploaded</dt>
                <dd>
                  {new Date(selectedDocument.uploaded_at).toLocaleString()}
                </dd>
              </div>
              <div>
                <dt className="text-meta">Size</dt>
                <dd>{formatFileSize(selectedDocument.size)}</dd>
              </div>
              <div>
                <dt className="text-meta">Indexing</dt>
                <dd>
                  {statsByDocumentId[selectedDocument.document_id]?.chunk_count ??
                    0}{" "}
                  chunks
                </dd>
              </div>
            </dl>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
