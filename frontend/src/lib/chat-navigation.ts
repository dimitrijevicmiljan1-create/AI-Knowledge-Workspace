import { listChats } from "@/lib/api/chat";
import type { ChatListResponse } from "@/lib/api/types";
import { routes } from "@/lib/routes";

export function chatDetailPath(chatId: string): string {
  return `${routes.chat}/${chatId}`;
}

export function resolveChatHomePath(chats: ChatListResponse | undefined): string {
  const mostRecent = chats?.items[0];
  return mostRecent ? chatDetailPath(mostRecent.id) : routes.chatNew;
}

export async function resolveChatEntryPath(): Promise<string> {
  try {
    const chats = await listChats();
    return resolveChatHomePath(chats);
  } catch {
    return routes.chatNew;
  }
}
