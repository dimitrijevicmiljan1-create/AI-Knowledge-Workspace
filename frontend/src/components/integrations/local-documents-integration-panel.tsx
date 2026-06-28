"use client";

import Link from "next/link";
import { FileText } from "lucide-react";

import { DocumentUpload } from "@/components/sources/document-upload";
import { DocumentsList } from "@/components/sources/documents-list";
import { IntegrationCard } from "@/components/integrations/integration-card";
import { buttonVariants } from "@/components/ui/button";
import {
  useDeleteUpload,
  useDocumentStats,
  useUploadDocuments,
  useUploads,
} from "@/hooks/use-sources";
import { getUsageStats } from "@/lib/api/settings";
import { routes } from "@/lib/routes";
import { cn } from "@/lib/utils";
import { useQuery } from "@tanstack/react-query";

type LocalDocumentsIntegrationPanelProps = {
  isExpanded: boolean;
  onToggle: () => void;
};

export function LocalDocumentsIntegrationPanel({
  isExpanded,
  onToggle,
}: LocalDocumentsIntegrationPanelProps) {
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

  const documentCount = usage?.documents ?? uploads?.total ?? 0;
  const indexedChunks = usage?.chunks ?? 0;
  const isConnected = documentCount > 0;

  return (
    <>
      <IntegrationCard
        name="Local Documents"
        description="Upload PDF, DOCX, Markdown, and text files for indexing and chat retrieval."
        icon={FileText}
        status={isConnected ? "connected" : "disconnected"}
        stats={[
          {
            label: "Documents",
            value: String(documentCount),
          },
          {
            label: "Indexed chunks",
            value: String(indexedChunks),
          },
        ]}
        connectLabel="Upload files"
        onConnect={onToggle}
        manageLabel={isExpanded ? "Hide details" : "Manage"}
        onManage={onToggle}
        isExpanded={isExpanded}
      />

      {isExpanded ? (
        <div className="col-span-full space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm text-text-secondary">
              Upload and manage documents in your workspace.
            </p>
            <Link
              href={routes.documents}
              className={cn(buttonVariants({ variant: "secondary", size: "sm" }))}
            >
              Open documents page
            </Link>
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
        </div>
      ) : null}
    </>
  );
}
