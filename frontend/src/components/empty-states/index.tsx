"use client";

import {
  BookMarked,
  FileText,
  FolderGit2,
  Layers,
  MessageSquare,
} from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";
import { routes } from "@/lib/routes";

export function NoChatsEmptyState() {
  return (
    <EmptyState
      icon={<MessageSquare className="size-6 text-muted-foreground" aria-hidden="true" />}
      title="No chats yet"
      description="Start a conversation to ask questions about your connected knowledge sources. Answers include citations from your workspace."
    />
  );
}

export function NoSourcesEmptyState() {
  return (
    <EmptyState
      icon={<Layers className="size-6 text-muted-foreground" aria-hidden="true" />}
      title="No sources connected"
      description="Connect documents, GitHub repositories, or Obsidian vaults to build your knowledge base."
      actionLabel="Browse sources"
      actionHref={routes.sources}
    />
  );
}

export function NoGithubEmptyState() {
  return (
    <EmptyState
      icon={<FolderGit2 className="size-6 text-muted-foreground" aria-hidden="true" />}
      title="No GitHub repositories"
      description="Connect a GitHub repository to index code and documentation into your workspace."
    />
  );
}

export function NoObsidianEmptyState() {
  return (
    <EmptyState
      icon={<BookMarked className="size-6 text-muted-foreground" aria-hidden="true" />}
      title="No Obsidian vaults"
      description="Connect an Obsidian vault to search and chat with your notes."
    />
  );
}

export function NoDocumentsEmptyState() {
  return (
    <EmptyState
      icon={<FileText className="size-6 text-muted-foreground" aria-hidden="true" />}
      title="No documents"
      description="Upload documents to make them searchable and available for RAG chat."
    />
  );
}
