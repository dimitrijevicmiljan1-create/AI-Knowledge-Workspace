"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";

import type { ChatMessage } from "@/components/chat/chat-thread";
import { getChatMessages, sendChatMessage } from "@/lib/api/chat";
import {
  syncChatTitleFromMessage,
  useCreateChat,
} from "@/hooks/use-chats";

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
    onSuccess: (_response, message) => {
      if (!chatId) {
        return;
      }
      syncChatTitleFromMessage(queryClient, chatId, message);
      queryClient.invalidateQueries({ queryKey: chatMessagesQueryKey(chatId) });
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

export function useDraftChatActions() {
  const queryClient = useQueryClient();
  const createChatMutation = useCreateChat();

  const sendMutation = useMutation({
    mutationFn: async (message: string) => {
      const trimmed = message.trim();
      if (!trimmed) {
        throw new Error("Message is required");
      }
      const chat = await createChatMutation.mutateAsync(undefined);
      await sendChatMessage(chat.id, trimmed);
      return chat.id;
    },
    onSuccess: (chatId, message) => {
      syncChatTitleFromMessage(queryClient, chatId, message);
      queryClient.invalidateQueries({ queryKey: chatMessagesQueryKey(chatId) });
    },
  });

  const sendFirstMessage = useCallback(
    async (message: string) => {
      const trimmed = message.trim();
      if (!trimmed) {
        return null;
      }
      return sendMutation.mutateAsync(trimmed);
    },
    [sendMutation],
  );

  return {
    sendFirstMessage,
    isSending: sendMutation.isPending || createChatMutation.isPending,
    error: sendMutation.error ?? createChatMutation.error,
  };
}
