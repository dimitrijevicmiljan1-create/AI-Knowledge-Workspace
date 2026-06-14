import { BookMarked, FileText, FolderGit2, MoreHorizontal } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type SourceType = "document" | "github" | "obsidian";

export type SourceCardProps = {
  type: SourceType;
  title: string;
  status: string;
  syncInfo?: string;
  metadata?: string;
  onAction?: () => void;
  actionLabel?: string;
  className?: string;
};

const typeConfig: Record<
  SourceType,
  { icon: typeof FileText; label: string; accent: string }
> = {
  document: {
    icon: FileText,
    label: "Document",
    accent: "text-primary",
  },
  github: {
    icon: FolderGit2,
    label: "GitHub",
    accent: "text-accent-secondary",
  },
  obsidian: {
    icon: BookMarked,
    label: "Obsidian",
    accent: "text-accent-secondary",
  },
};

export function SourceCard({
  type,
  title,
  status,
  syncInfo,
  metadata,
  onAction,
  actionLabel,
  className,
}: SourceCardProps) {
  const config = typeConfig[type];
  const Icon = config.icon;

  return (
    <article
      className={cn(
        "group surface-panel flex flex-col gap-3 p-4 transition-all duration-200 hover:border-primary/25 hover:shadow-[0_8px_32px_rgba(0,0,0,0.25)]",
        className,
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-3">
          <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-surface">
            <Icon className={cn("size-5", config.accent)} aria-hidden="true" />
          </div>
          <div className="min-w-0">
            <p className="text-meta">{config.label}</p>
            <h3 className="truncate text-sm font-semibold">{title}</h3>
          </div>
        </div>
        <Button variant="ghost" size="icon-sm" aria-label="Source actions">
          <MoreHorizontal className="size-4" />
        </Button>
      </div>
      <div className="flex flex-wrap items-center gap-2 text-meta">
        <span className="rounded-md border border-border bg-surface px-2 py-0.5">
          {status}
        </span>
        {syncInfo ? <span>{syncInfo}</span> : null}
        {metadata ? <span className="truncate">{metadata}</span> : null}
      </div>
      {actionLabel && onAction ? (
        <Button variant="secondary" size="sm" className="w-full" onClick={onAction}>
          {actionLabel}
        </Button>
      ) : null}
    </article>
  );
}
