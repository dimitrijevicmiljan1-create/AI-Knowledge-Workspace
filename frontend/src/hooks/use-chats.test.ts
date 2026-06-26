import { describe, expect, it, vi } from "vitest";
import { QueryClient } from "@tanstack/react-query";

import {
  chatsQueryKey,
  prependChatToCache,
  removeChatFromCache,
  syncChatTitleFromMessage,
} from "@/hooks/use-chats";
import type { ChatListResponse } from "@/lib/api/types";

describe("use-chats cache helpers", () => {
  it("prepends a created chat without invalidating the query", () => {
    const queryClient = new QueryClient();
    const existing: ChatListResponse = {
      items: [
        {
          id: "chat-1",
          workspace_id: "ws-1",
          title: "Existing",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      total: 1,
    };

    queryClient.setQueryData(chatsQueryKey, existing);
    const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");

    prependChatToCache(queryClient, { id: "chat-2" });

    const updated = queryClient.getQueryData<ChatListResponse>(chatsQueryKey);
    expect(updated?.items.map((item) => item.id)).toEqual(["chat-2", "chat-1"]);
    expect(updated?.total).toBe(2);
    expect(invalidateSpy).not.toHaveBeenCalled();
  });

  it("removes a deleted chat from the cache", () => {
    const queryClient = new QueryClient();
    queryClient.setQueryData<ChatListResponse>(chatsQueryKey, {
      items: [
        {
          id: "chat-1",
          workspace_id: "ws-1",
          title: "Keep",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
        {
          id: "chat-2",
          workspace_id: "ws-1",
          title: "Delete",
          created_at: "2026-01-02T00:00:00Z",
          updated_at: "2026-01-02T00:00:00Z",
        },
      ],
      total: 2,
    });

    removeChatFromCache(queryClient, "chat-2");

    const updated = queryClient.getQueryData<ChatListResponse>(chatsQueryKey);
    expect(updated?.items).toHaveLength(1);
    expect(updated?.items[0]?.id).toBe("chat-1");
    expect(updated?.total).toBe(1);
  });

  it("updates the sidebar title from the first user message", () => {
    const queryClient = new QueryClient();
    queryClient.setQueryData<ChatListResponse>(chatsQueryKey, {
      items: [
        {
          id: "chat-1",
          workspace_id: "ws-1",
          title: "New chat",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      total: 1,
    });

    syncChatTitleFromMessage(queryClient, "chat-1", "Upload pipeline");

    const updated = queryClient.getQueryData<ChatListResponse>(chatsQueryKey);
    expect(updated?.items[0]?.title).toBe("Upload pipeline");
  });
});
