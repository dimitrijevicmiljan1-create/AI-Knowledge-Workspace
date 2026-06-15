"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createChat,
  deleteChat,
  listChats,
} from "@/lib/api/chat";
import { hasStoredSession } from "@/lib/auth-storage";

export const chatsQueryKey = ["chats"] as const;

export function useChats() {
  return useQuery({
    queryKey: chatsQueryKey,
    queryFn: listChats,
    enabled: hasStoredSession(),
    refetchInterval: 30_000,
  });
}

export function useCreateChat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (title?: string) => createChat(title),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: chatsQueryKey });
    },
  });
}

export function useDeleteChat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (chatId: string) => deleteChat(chatId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: chatsQueryKey });
    },
  });
}
