"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { ChatComposer } from "@/components/chat/chat-composer";
import { ChatThread } from "@/components/chat/chat-thread";
import { NoChatsEmptyState } from "@/components/empty-states";
import { ErrorBanner } from "@/components/ui/error-banner";
import { Skeleton } from "@/components/ui/skeleton";
import { useChatActions, useDraftChatActions } from "@/hooks/use-chat";
import { useChats } from "@/hooks/use-chats";
import { getLastChatId, setLastChatId } from "@/lib/chat-storage";
import { getErrorMessage } from "@/lib/errors";
import { routes } from "@/lib/routes";

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

  useEffect(() => {
    setLastChatId(chatId);
  }, [chatId]);

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

export function ChatDraftView() {
  const router = useRouter();
  const { sendFirstMessage, isSending, error } = useDraftChatActions();

  async function handleSubmit(message: string) {
    const chatId = await sendFirstMessage(message);
    if (chatId) {
      router.replace(`${routes.chat}/${chatId}`);
    }
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col overflow-hidden rounded-2xl border border-border bg-surface">
      {error ? (
        <div className="px-4 pt-4 sm:px-6">
          <ErrorBanner
            message={getErrorMessage(error, "Unable to start conversation.")}
          />
        </div>
      ) : null}

      <div className="flex flex-1 items-center justify-center overflow-auto p-6">
        <NoChatsEmptyState />
      </div>
      <ChatComposer
        onSubmit={(message) => void handleSubmit(message)}
        isLoading={isSending}
      />
    </div>
  );
}

export function ChatLanding() {
  const router = useRouter();
  const { data, isLoading, error } = useChats();

  useEffect(() => {
    if (isLoading || !data?.items.length) {
      return;
    }

    const lastChatId = getLastChatId();
    const hasLastChat = lastChatId
      ? data.items.some((chat) => chat.id === lastChatId)
      : false;
    const targetChatId = hasLastChat ? lastChatId! : data.items[0].id;

    router.replace(`${routes.chat}/${targetChatId}`);
  }, [data, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
        <Skeleton className="h-8 w-48" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-[calc(100vh-4rem)] items-center justify-center p-6">
        <ErrorBanner
          message={getErrorMessage(error, "Unable to load conversations.")}
        />
      </div>
    );
  }

  if (!data?.items.length) {
    return <ChatDraftView />;
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
      <Skeleton className="h-8 w-48" />
    </div>
  );
}
