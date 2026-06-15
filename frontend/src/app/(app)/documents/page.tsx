"use client";

import { DocumentUpload } from "@/components/sources/document-upload";
import { DocumentsList } from "@/components/sources/documents-list";
import { PageHeader } from "@/components/layout/page-header";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useDeleteUpload,
  useDocumentStats,
  useUploadDocuments,
  useUploads,
} from "@/hooks/use-sources";
import { useUserWorkspace } from "@/hooks/use-user-workspace";
import { getUsageStats } from "@/lib/api/settings";
import { useQuery } from "@tanstack/react-query";

export default function DocumentsPage() {
  const { isLoading: isWorkspaceLoading } = useUserWorkspace();
  const {
    data: uploads,
    isLoading: isUploadsLoading,
    isFetching,
    error: uploadsError,
    refetch,
  } = useUploads();
  const uploadDocuments = useUploadDocuments();
  const deleteUpload = useDeleteUpload();

  const documentIds = uploads?.items.map((file) => file.document_id) ?? [];
  const { data: statsByDocumentId = {} } = useDocumentStats(documentIds);

  const { data: usage } = useQuery({
    queryKey: ["usage-stats"],
    queryFn: getUsageStats,
  });

  if (isWorkspaceLoading) {
    return (
      <section className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-40 w-full" />
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <PageHeader
        title="Documents"
        description="Upload and manage documents in your personal knowledge workspace."
      />

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-xl border border-border bg-surface p-4">
          <p className="text-meta">Documents</p>
          <p className="text-sm font-semibold">
            {usage?.documents ?? uploads?.total ?? 0}
          </p>
        </div>
        <div className="rounded-xl border border-border bg-surface p-4">
          <p className="text-meta">Indexed chunks</p>
          <p className="text-sm font-semibold">{usage?.chunks ?? 0}</p>
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
