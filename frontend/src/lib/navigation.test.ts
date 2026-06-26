import { describe, expect, it } from "vitest";
import { QueryClient } from "@tanstack/react-query";

import {
  chatsQueryKey,
  DEFAULT_CHAT_TITLE,
  syncChatTitleFromMessage,
  updateChatTitleInCache,
} from "@/hooks/use-chats";
import type { ChatListResponse } from "@/lib/api/types";
import {
  deriveChatTitle,
  getBackFallbackPath,
  shouldShowBackButton,
} from "@/lib/navigation";
import { routes } from "@/lib/routes";

describe("deriveChatTitle", () => {
  it("uses the first line of the message and truncates to 80 characters", () => {
    const longLine = "a".repeat(100);
    expect(deriveChatTitle(`  ${longLine}\nsecond line`)).toHaveLength(80);
    expect(deriveChatTitle("How does the upload pipeline work?")).toBe(
      "How does the upload pipeline work?",
    );
  });

  it("falls back to the default title for blank messages", () => {
    expect(deriveChatTitle("   ")).toBe(DEFAULT_CHAT_TITLE);
  });
});

describe("chat title cache helpers", () => {
  it("updates only chats that still use the default title", () => {
    const queryClient = new QueryClient();
    queryClient.setQueryData<ChatListResponse>(chatsQueryKey, {
      items: [
        {
          id: "chat-1",
          workspace_id: "ws-1",
          title: DEFAULT_CHAT_TITLE,
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
        {
          id: "chat-2",
          workspace_id: "ws-1",
          title: "Renamed chat",
          created_at: "2026-01-02T00:00:00Z",
          updated_at: "2026-01-02T00:00:00Z",
        },
      ],
      total: 2,
    });

    syncChatTitleFromMessage(
      queryClient,
      "chat-1",
      "Upload pipeline overview",
    );

    const updated = queryClient.getQueryData<ChatListResponse>(chatsQueryKey);
    expect(updated?.items[0]?.title).toBe("Upload pipeline overview");
    expect(updated?.items[1]?.title).toBe("Renamed chat");
  });

  it("does not overwrite a manually renamed title", () => {
    const queryClient = new QueryClient();
    queryClient.setQueryData<ChatListResponse>(chatsQueryKey, {
      items: [
        {
          id: "chat-1",
          workspace_id: "ws-1",
          title: "Custom title",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      total: 1,
    });

    updateChatTitleInCache(queryClient, "chat-1", "Should not apply");

    const updated = queryClient.getQueryData<ChatListResponse>(chatsQueryKey);
    expect(updated?.items[0]?.title).toBe("Custom title");
  });
});

describe("back navigation helpers", () => {
  it("shows a back button on detail and knowledge pages", () => {
    expect(shouldShowBackButton("/chat/123")).toBe(true);
    expect(shouldShowBackButton(routes.documents)).toBe(true);
    expect(shouldShowBackButton(routes.sources)).toBe(true);
    expect(shouldShowBackButton(routes.settings)).toBe(true);
    expect(shouldShowBackButton(routes.chatNew)).toBe(false);
    expect(shouldShowBackButton(routes.chat)).toBe(false);
  });

  it("uses chat entry as the fallback parent for knowledge pages", () => {
    expect(getBackFallbackPath(routes.documents)).toBe(routes.chatNew);
    expect(getBackFallbackPath("/chat/123")).toBe(routes.chatNew);
  });
});
