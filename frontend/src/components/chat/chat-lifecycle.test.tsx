import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";

import { ChatDraftView, ChatPageContent } from "@/components/chat/chat-page-content";
import NewChatPage from "@/app/(app)/chat/new/page";
import ChatPage from "@/app/(app)/chat/page";
import { renderWithProviders } from "@/test/test-utils";

const createChat = vi.fn();
const listChats = vi.fn();
const getChatMessages = vi.fn();
const sendChatMessage = vi.fn();
const replace = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace, push: vi.fn() }),
}));

vi.mock("@/lib/api/chat", () => ({
  createChat: (...args: unknown[]) => createChat(...args),
  listChats: (...args: unknown[]) => listChats(...args),
  getChatMessages: (...args: unknown[]) => getChatMessages(...args),
  sendChatMessage: (...args: unknown[]) => sendChatMessage(...args),
  deleteChat: vi.fn(),
}));

describe("chat lifecycle", () => {
  beforeEach(() => {
    createChat.mockReset();
    listChats.mockReset();
    getChatMessages.mockReset();
    sendChatMessage.mockReset();
    replace.mockReset();

    listChats.mockResolvedValue({ items: [], total: 0 });
    getChatMessages.mockResolvedValue({ items: [], total: 0 });
  });

  it("does not create chats when /chat mounts", () => {
    renderWithProviders(<ChatPage />);

    expect(createChat).not.toHaveBeenCalled();
    expect(listChats).not.toHaveBeenCalled();
    expect(screen.getByLabelText(/chat message/i)).toBeInTheDocument();
  });

  it("does not create chats when /chat/new mounts", () => {
    renderWithProviders(<NewChatPage />);

    expect(createChat).not.toHaveBeenCalled();
    expect(listChats).not.toHaveBeenCalled();
    expect(screen.getByText(/no chats yet/i)).toBeInTheDocument();
  });

  it("does not create chats when ChatDraftView mounts", () => {
    renderWithProviders(<ChatDraftView />);

    expect(createChat).not.toHaveBeenCalled();
  });

  it("does not create chats when an existing chat page mounts", () => {
    renderWithProviders(<ChatPageContent chatId="chat-123" />);

    expect(createChat).not.toHaveBeenCalled();
    expect(getChatMessages).toHaveBeenCalledWith("chat-123");
  });
});
