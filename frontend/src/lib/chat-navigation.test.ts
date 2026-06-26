import { describe, expect, it, vi } from "vitest";

import { resolveChatHomePath, resolveChatEntryPath } from "@/lib/chat-navigation";
import type { ChatListResponse } from "@/lib/api/types";

vi.mock("@/lib/api/chat", () => ({
  listChats: vi.fn(),
}));

import { listChats } from "@/lib/api/chat";

const listChatsMock = vi.mocked(listChats);

describe("chat-navigation", () => {
  it("resolves home path to the most recent chat", () => {
    const chats: ChatListResponse = {
      items: [
        {
          id: "chat-1",
          workspace_id: "ws-1",
          title: "Latest",
          created_at: "2026-01-02T00:00:00Z",
          updated_at: "2026-01-02T00:00:00Z",
        },
        {
          id: "chat-2",
          workspace_id: "ws-1",
          title: "Older",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      total: 2,
    };

    expect(resolveChatHomePath(chats)).toBe("/chat/chat-1");
  });

  it("resolves home path to draft workspace when there are no chats", () => {
    expect(resolveChatHomePath({ items: [], total: 0 })).toBe("/chat/new");
    expect(resolveChatHomePath(undefined)).toBe("/chat/new");
  });

  it("resolves entry path from the API without creating chats", async () => {
    listChatsMock.mockResolvedValueOnce({
      items: [
        {
          id: "chat-99",
          workspace_id: "ws-1",
          title: "Existing",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z",
        },
      ],
      total: 1,
    });

    await expect(resolveChatEntryPath()).resolves.toBe("/chat/chat-99");
    expect(listChatsMock).toHaveBeenCalledTimes(1);
  });

  it("falls back to draft workspace when chat list cannot be loaded", async () => {
    listChatsMock.mockRejectedValueOnce(new Error("network"));

    await expect(resolveChatEntryPath()).resolves.toBe("/chat/new");
  });
});
