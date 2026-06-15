"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";

import type { ChatMessage } from "@/components/chat/chat-thread";
import { getChatMessages, sendChatMessage } from "@/lib/api/chat";
import { chatsQueryKey } from "@/hooks/use-chats";

export const chatMessagesQueryKey = (chatId: string) =>
  ["chat-messages", chatId] as const;

function toChatMessage(item: {
  id: string;
  role: string;
  content: string;
}): ChatMessage {
  return {
    id: item.id,
    role: item.role as "user" | "assistant",
    content: item.content,
  };
}

export function useChatMessages(chatId: string | null) {
  return useQuery({
    queryKey: chatMessagesQueryKey(chatId ?? "none"),
    queryFn: async () => {
      const response = await getChatMessages(chatId!);
      return response.items.map((item) => toChatMessage(item));
    },
    enabled: Boolean(chatId),
  });
}

export function useChatActions(chatId: string | null) {
  const queryClient = useQueryClient();
  const {
    data: messages = [],
    isLoading,
    error,
    refetch,
  } = useChatMessages(chatId);

  const sendMutation = useMutation({
    mutationFn: async (message: string) => {
      if (!chatId) {
        throw new Error("No chat selected");
      }
      return sendChatMessage(chatId, message);
    },
    onSuccess: () => {
      if (!chatId) {
        return;
      }
      queryClient.invalidateQueries({ queryKey: chatMessagesQueryKey(chatId) });
      queryClient.invalidateQueries({ queryKey: chatsQueryKey });
    },
  });

  const sendMessage = useCallback(
    async (message: string) => {
      const trimmed = message.trim();
      if (!trimmed || !chatId) {
        return;
      }
      await sendMutation.mutateAsync(trimmed);
    },
    [chatId, sendMutation],
  );

  return {
    messages,
    isLoading,
    error,
    refetch,
    sendMessage,
    isSending: sendMutation.isPending,
    sendError: sendMutation.error,
  };
}
