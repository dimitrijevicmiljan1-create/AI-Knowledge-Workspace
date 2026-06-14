export type StoredChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Array<{
    id: string;
    documentTitle: string;
    filePath?: string | null;
    repositoryName?: string | null;
  }>;
};

function sessionKey(workspaceId: string): string {
  return `chat_session_${workspaceId}`;
}

function messagesKey(sessionId: string): string {
  return `chat_messages_${sessionId}`;
}

export function getStoredSessionId(workspaceId: string): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem(sessionKey(workspaceId));
}

export function setStoredSessionId(workspaceId: string, sessionId: string): void {
  localStorage.setItem(sessionKey(workspaceId), sessionId);
}

export function clearStoredSessionId(workspaceId: string): void {
  localStorage.removeItem(sessionKey(workspaceId));
}

export function getStoredMessages(sessionId: string): StoredChatMessage[] {
  if (typeof window === "undefined") {
    return [];
  }
  const raw = localStorage.getItem(messagesKey(sessionId));
  if (!raw) {
    return [];
  }
  try {
    return JSON.parse(raw) as StoredChatMessage[];
  } catch {
    return [];
  }
}

export function setStoredMessages(
  sessionId: string,
  messages: StoredChatMessage[],
): void {
  localStorage.setItem(messagesKey(sessionId), JSON.stringify(messages));
}

export function clearStoredMessages(sessionId: string): void {
  localStorage.removeItem(messagesKey(sessionId));
}
