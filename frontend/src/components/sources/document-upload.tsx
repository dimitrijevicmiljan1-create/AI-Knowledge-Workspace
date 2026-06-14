"use client";

import { FileUp, Upload } from "lucide-react";
import { useCallback, useRef, useState } from "react";

import { ErrorBanner } from "@/components/ui/error-banner";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { isAllowedUploadFile } from "@/lib/api/sources";
import { getErrorMessage } from "@/lib/errors";

type DocumentUploadProps = {
  onUpload: (files: File[]) => Promise<void>;
  isUploading?: boolean;
  className?: string;
};

const ACCEPT = ".txt,.md,.pdf,.docx";

export function DocumentUpload({
  onUpload,
  isUploading = false,
  className,
}: DocumentUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processFiles = useCallback(
    async (fileList: FileList | File[]) => {
      const files = Array.from(fileList);
      const validFiles = files.filter(isAllowedUploadFile);
      const invalidCount = files.length - validFiles.length;

      if (validFiles.length === 0) {
        setError("Only .txt, .md, .pdf, and .docx files are supported.");
        return;
      }

      setError(
        invalidCount > 0
          ? `${invalidCount} unsupported file(s) were skipped. Supported formats: .txt, .md, .pdf, .docx`
          : null,
      );

      try {
        await onUpload(validFiles);
      } catch (uploadError) {
        setError(getErrorMessage(uploadError, "Upload failed."));
      }
    },
    [onUpload],
  );

  return (
    <div className={cn("space-y-3", className)}>
      <div
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setIsDragging(false);
          if (!isUploading) {
            void processFiles(event.dataTransfer.files);
          }
        }}
        className={cn(
          "flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed px-6 py-10 text-center transition-colors",
          isDragging
            ? "border-primary bg-primary/5"
            : "border-border bg-surface/50",
        )}
      >
        <div className="flex size-12 items-center justify-center rounded-xl bg-elevated">
          <Upload className="size-5 text-primary" aria-hidden="true" />
        </div>
        <div className="space-y-1">
          <p className="text-sm font-medium">Drag and drop documents here</p>
          <p className="text-meta">
            Supported formats: TXT, Markdown, PDF, DOCX (max 20 MB)
          </p>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-2">
          <Button
            type="button"
            variant="secondary"
            disabled={isUploading}
            onClick={() => inputRef.current?.click()}
          >
            <FileUp className="size-4" />
            {isUploading ? "Uploading…" : "Choose files"}
          </Button>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPT}
          multiple
          className="hidden"
          aria-label="Upload documents"
          onChange={(event) => {
            if (event.target.files?.length) {
              void processFiles(event.target.files);
              event.target.value = "";
            }
          }}
        />
      </div>
      {error ? <ErrorBanner message={error} /> : null}
    </div>
  );
}
