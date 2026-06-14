"use client";

import { Loader2, MessageSquarePlus } from "lucide-react";

import { ChatComposer } from "@/components/chat/chat-composer";
import { ChatThread } from "@/components/chat/chat-thread";
import { NoChatsEmptyState } from "@/components/empty-states";
import { ErrorBanner } from "@/components/ui/error-banner";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useChatSession } from "@/hooks/use-chat";
import { useActiveWorkspace } from "@/hooks/use-active-workspace";
import { getErrorMessage } from "@/lib/errors";

export function ChatPageContent() {
  const { activeWorkspace, isLoading: isWorkspaceLoading } = useActiveWorkspace();
  const {
    messages,
    isInitializing,
    initError,
    isSending,
    sendError,
    sendMessage,
    startNewSession,
  } = useChatSession();

  if (isWorkspaceLoading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] flex-col gap-4 p-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="flex-1 w-full" />
      </div>
    );
  }

  if (!activeWorkspace) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center p-6">
        <p className="text-sm text-text-secondary">
          Create a workspace to start chatting with your knowledge base.
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col overflow-hidden rounded-2xl border border-border bg-surface">
      <div className="flex items-center justify-between gap-3 border-b border-border px-4 py-4 sm:px-6">
        <div>
          <h1 className="text-lg font-semibold">Chat</h1>
          <p className="text-sm text-text-secondary">
            Ask questions about {activeWorkspace.name}. Answers include citations
            from indexed sources.
          </p>
        </div>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          onClick={() => void startNewSession()}
          disabled={isInitializing || isSending}
        >
          <MessageSquarePlus className="size-4" />
          New chat
        </Button>
      </div>

      {initError ? (
        <div className="px-4 pt-4 sm:px-6">
          <ErrorBanner message={initError} />
        </div>
      ) : null}

      {sendError ? (
        <div className="px-4 pt-4 sm:px-6">
          <ErrorBanner
            message={getErrorMessage(sendError, "Unable to send message.")}
          />
        </div>
      ) : null}

      {isInitializing ? (
        <div className="flex flex-1 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-text-secondary" />
        </div>
      ) : (
        <ChatThread
          messages={messages}
          isTyping={isSending}
          emptyState={<NoChatsEmptyState />}
        />
      )}

      <ChatComposer
        onSubmit={(message) => void sendMessage(message)}
        disabled={isInitializing || Boolean(initError)}
        isLoading={isSending}
      />
    </div>
  );
}
