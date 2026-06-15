"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { ChatComposer } from "@/components/chat/chat-composer";
import { ChatThread } from "@/components/chat/chat-thread";
import { NoChatsEmptyState } from "@/components/empty-states";
import { ErrorBanner } from "@/components/ui/error-banner";
import { Skeleton } from "@/components/ui/skeleton";
import { useChatActions } from "@/hooks/use-chat";
import { getErrorMessage } from "@/lib/errors";

type ChatPageContentProps = {
  chatId: string;
};

export function ChatPageContent({ chatId }: ChatPageContentProps) {
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    isSending,
    sendError,
  } = useChatActions(chatId);

  if (isLoading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] flex-col gap-4 p-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="flex-1 w-full" />
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col overflow-hidden rounded-2xl border border-border bg-surface">
      {error ? (
        <div className="px-4 pt-4 sm:px-6">
          <ErrorBanner
            message={getErrorMessage(error, "Unable to load conversation.")}
          />
        </div>
      ) : null}
      {sendError ? (
        <div className="px-4 pt-4 sm:px-6">
          <ErrorBanner
            message={getErrorMessage(sendError, "Unable to send message.")}
          />
        </div>
      ) : null}

      <ChatThread
        messages={messages}
        isTyping={isSending}
        emptyState={<NoChatsEmptyState />}
      />
      <ChatComposer
        onSubmit={(message) => void sendMessage(message)}
        isLoading={isSending}
      />
    </div>
  );
}

export function NewChatRedirect() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/chat/new");
  }, [router]);

  return (
    <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
      <Skeleton className="h-8 w-48" />
    </div>
  );
}
