import { FileText, Quote } from "lucide-react";

import { cn } from "@/lib/utils";

export type Citation = {
  id: string;
  documentTitle: string;
  filePath?: string | null;
};

export function CitationBadge({
  citation,
  className,
}: {
  citation: Citation;
  className?: string;
}) {
  return (
    <button
      type="button"
      className={cn(
        "inline-flex max-w-full items-center gap-1.5 rounded-lg border border-primary/25 bg-primary/10 px-2 py-1 text-left text-xs text-primary transition-colors hover:bg-primary/15",
        className,
      )}
      title={citation.filePath ?? citation.documentTitle}
    >
      <Quote className="size-3 shrink-0" aria-hidden="true" />
      <span className="truncate">{citation.documentTitle}</span>
    </button>
  );
}

export function CitationList({ citations }: { citations: Citation[] }) {
  if (citations.length === 0) return null;

  return (
    <div className="mt-3 flex flex-wrap gap-2" aria-label="Citations">
      {citations.map((citation) => (
        <CitationBadge key={citation.id} citation={citation} />
      ))}
    </div>
  );
}

export function CitationPlaceholder() {
  return (
    <div className="mt-3 inline-flex items-center gap-1.5 rounded-lg border border-dashed border-border px-2 py-1 text-meta">
      <FileText className="size-3" aria-hidden="true" />
      Citations appear here when available
    </div>
  );
}
