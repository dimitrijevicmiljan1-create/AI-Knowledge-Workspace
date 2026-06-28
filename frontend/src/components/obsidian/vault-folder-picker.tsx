"use client";

import { FolderOpen, Loader2 } from "lucide-react";
import { useRef, useState } from "react";

import { ErrorBanner } from "@/components/ui/error-banner";
import { Button } from "@/components/ui/button";
import { filterMarkdownFiles } from "@/lib/api/obsidian";
import { getErrorMessage } from "@/lib/errors";

type VaultFolderPickerProps = {
  onSelect: (files: File[]) => Promise<void>;
  isLoading?: boolean;
  disabled?: boolean;
};

export function VaultFolderPicker({
  onSelect,
  isLoading = false,
  disabled = false,
}: VaultFolderPickerProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleChange(event: React.ChangeEvent<HTMLInputElement>) {
    const fileList = event.target.files;
    if (!fileList?.length) {
      return;
    }

    const markdownFiles = filterMarkdownFiles(Array.from(fileList));
    if (markdownFiles.length === 0) {
      setError("No markdown (.md) files found in the selected folder.");
      event.target.value = "";
      return;
    }

    setError(null);
    try {
      await onSelect(markdownFiles);
    } catch (selectError) {
      setError(getErrorMessage(selectError, "Unable to connect vault folder."));
    } finally {
      event.target.value = "";
    }
  }

  return (
    <div className="space-y-3">
      <input
        ref={inputRef}
        type="file"
        accept=".md"
        multiple
        className="hidden"
        // @ts-expect-error webkitdirectory is supported by Chromium-based browsers.
        webkitdirectory=""
        directory=""
        onChange={(event) => void handleChange(event)}
      />

      <Button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={disabled || isLoading}
      >
        {isLoading ? (
          <Loader2 className="size-4 animate-spin" />
        ) : (
          <FolderOpen className="size-4" />
        )}
        Choose vault folder
      </Button>

      <p className="text-meta">
        Select your Obsidian vault folder. Only markdown notes will be indexed.
      </p>

      {error ? <ErrorBanner message={error} /> : null}
    </div>
  );
}
