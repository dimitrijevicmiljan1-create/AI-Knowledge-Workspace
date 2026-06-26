const LAST_CHAT_ID_KEY = "last_chat_id";

export function getLastChatId(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem(LAST_CHAT_ID_KEY);
}

export function setLastChatId(chatId: string): void {
  localStorage.setItem(LAST_CHAT_ID_KEY, chatId);
}

export function clearLastChatId(): void {
  localStorage.removeItem(LAST_CHAT_ID_KEY);
}
