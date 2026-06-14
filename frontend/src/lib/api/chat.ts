import { apiRequest } from "@/lib/api/client";
import type {
  ApiCitation,
  ChatSessionCreateResponse,
  SessionMessageResponse,
} from "@/lib/api/types";
import type { Citation } from "@/components/chat/citation-badge";

export type CreateChatSessionPayload = {
  workspace_id: string;
  title?: string;
};

export async function createChatSession(
  payload: CreateChatSessionPayload,
): Promise<ChatSessionCreateResponse> {
  return apiRequest<ChatSessionCreateResponse>("/chat/session", {
    method: "POST",
    body: payload,
  });
}

export type SendSessionMessagePayload = {
  message: string;
  top_k?: number;
};

export async function sendSessionMessage(
  sessionId: string,
  payload: SendSessionMessagePayload,
): Promise<SessionMessageResponse> {
  return apiRequest<SessionMessageResponse>(
    `/chat/session/${sessionId}/message`,
    {
      method: "POST",
      body: payload,
    },
  );
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
