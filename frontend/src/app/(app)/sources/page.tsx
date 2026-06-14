"use client";

import { DocumentUpload } from "@/components/sources/document-upload";
import { DocumentsList } from "@/components/sources/documents-list";
import { PageHeader } from "@/components/layout/page-header";
import { Skeleton } from "@/components/ui/skeleton";
import { useActiveWorkspace } from "@/hooks/use-active-workspace";
import {
  useDeleteUpload,
  useDocumentStats,
  useUploadDocuments,
  useUploads,
} from "@/hooks/use-sources";
import { getWorkspaceStats } from "@/lib/api/workspaces";
import { useQuery } from "@tanstack/react-query";

export default function SourcesPage() {
  const { activeWorkspace, activeWorkspaceId, isLoading: isWorkspaceLoading } =
    useActiveWorkspace();
  const {
    data: uploads,
    isLoading: isUploadsLoading,
    isFetching,
    error: uploadsError,
    refetch,
  } = useUploads();
  const uploadDocuments = useUploadDocuments();
  const deleteUpload = useDeleteUpload();

  const documentIds =
    uploads?.items.map((file) => file.document_id) ?? [];

  const { data: statsByDocumentId = {} } = useDocumentStats(documentIds);

  const { data: workspaceStats } = useQuery({
    queryKey: ["workspace-stats", activeWorkspaceId],
    queryFn: () => getWorkspaceStats(activeWorkspaceId!),
    enabled: Boolean(activeWorkspaceId),
  });

  if (isWorkspaceLoading) {
    return (
      <section className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-40 w-full" />
      </section>
    );
  }

  if (!activeWorkspace) {
    return (
      <section className="space-y-6">
        <PageHeader
          title="Sources"
          description="Manage documents in your workspace."
        />
        <p className="text-sm text-text-secondary">
          Create a workspace to upload and manage documents.
        </p>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <PageHeader
        title="Sources"
        description="Upload documents and track indexing status for your active workspace."
      />

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-xl border border-border bg-surface p-4">
          <p className="text-meta">Workspace</p>
          <p className="text-sm font-semibold">{activeWorkspace.name}</p>
        </div>
        <div className="rounded-xl border border-border bg-surface p-4">
          <p className="text-meta">Documents</p>
          <p className="text-sm font-semibold">
            {workspaceStats?.document_count ?? uploads?.total ?? 0}
          </p>
        </div>
        <div className="rounded-xl border border-border bg-surface p-4">
          <p className="text-meta">Sources</p>
          <p className="text-sm font-semibold">
            {workspaceStats?.source_count ?? 0}
          </p>
        </div>
      </div>

      <DocumentUpload
        isUploading={uploadDocuments.isPending}
        onUpload={async (files) => {
          await uploadDocuments.mutateAsync(files);
        }}
      />

      <DocumentsList
        files={uploads?.items ?? []}
        statsByDocumentId={statsByDocumentId}
        isLoading={isUploadsLoading}
        isRefreshing={isFetching}
        onRefresh={() => void refetch()}
        onDelete={async (documentId) => {
          await deleteUpload.mutateAsync(documentId);
        }}
        error={uploadsError}
      />
    </section>
  );
}
