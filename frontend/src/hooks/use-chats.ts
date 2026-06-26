"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
  type QueryClient,
} from "@tanstack/react-query";

import {
  createChat,
  deleteChat,
  listChats,
} from "@/lib/api/chat";
import type { ChatCreateResponse, ChatListResponse } from "@/lib/api/types";
import { hasStoredSession } from "@/lib/auth-storage";

export const chatsQueryKey = ["chats"] as const;

const CHATS_STALE_TIME_MS = 5 * 60 * 1000;

export function useChats() {
  return useQuery({
    queryKey: chatsQueryKey,
    queryFn: listChats,
    enabled: hasStoredSession(),
    staleTime: CHATS_STALE_TIME_MS,
    refetchOnMount: false,
    refetchOnReconnect: false,
  });
}

export function prependChatToCache(
  queryClient: QueryClient,
  chat: ChatCreateResponse,
) {
  queryClient.setQueryData<ChatListResponse>(chatsQueryKey, (current) => {
    const now = new Date().toISOString();
    const summary = {
      id: chat.id,
      workspace_id: "",
      title: "New chat",
      created_at: now,
      updated_at: now,
    };

    if (!current) {
      return { items: [summary], total: 1 };
    }

    const withoutDuplicate = current.items.filter((item) => item.id !== chat.id);
    return {
      items: [summary, ...withoutDuplicate],
      total: withoutDuplicate.length + 1,
    };
  });
}

export function removeChatFromCache(queryClient: QueryClient, chatId: string) {
  queryClient.setQueryData<ChatListResponse>(chatsQueryKey, (current) => {
    if (!current) {
      return current;
    }

    const items = current.items.filter((item) => item.id !== chatId);
    return {
      items,
      total: items.length,
    };
  });
}

export function useCreateChat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (title?: string) => createChat(title),
    onSuccess: (chat) => {
      prependChatToCache(queryClient, chat);
    },
  });
}

export function useDeleteChat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (chatId: string) => deleteChat(chatId),
    onSuccess: (_result, chatId) => {
      removeChatFromCache(queryClient, chatId);
    },
  });
}
