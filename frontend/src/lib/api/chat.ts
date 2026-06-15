import { apiRequest } from "@/lib/api/client";
import type {
  ApiCitation,
  ChatCreateResponse,
  ChatListResponse,
  ChatMessageListResponse,
  ChatSummary,
  SessionMessageResponse,
} from "@/lib/api/types";
import type { Citation } from "@/components/chat/citation-badge";

export async function listChats(): Promise<ChatListResponse> {
  return apiRequest<ChatListResponse>("/chats");
}

export async function createChat(title?: string): Promise<ChatCreateResponse> {
  return apiRequest<ChatCreateResponse>("/chats", {
    method: "POST",
    body: title ? { title } : {},
  });
}

export async function getChat(chatId: string): Promise<ChatSummary> {
  return apiRequest<ChatSummary>(`/chats/${chatId}`);
}

export async function getChatMessages(
  chatId: string,
): Promise<ChatMessageListResponse> {
  return apiRequest<ChatMessageListResponse>(`/chats/${chatId}/messages`);
}

export async function deleteChat(chatId: string): Promise<void> {
  return apiRequest<void>(`/chats/${chatId}`, { method: "DELETE" });
}

export async function sendChatMessage(
  chatId: string,
  message: string,
): Promise<SessionMessageResponse> {
  return apiRequest<SessionMessageResponse>(`/chats/${chatId}/messages`, {
    method: "POST",
    body: { message },
  });
}

export function mapApiCitation(citation: ApiCitation): Citation {
  return {
    id: citation.chunk_id,
    documentTitle: citation.document_title,
    filePath: citation.file_path,
    repositoryName: citation.repository_name,
  };
}

export function mapApiCitations(citations: ApiCitation[]): Citation[] {
  return citations.map(mapApiCitation);
}
