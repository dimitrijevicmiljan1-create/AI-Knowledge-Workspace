"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useState } from "react";

import type { ChatMessage } from "@/components/chat/chat-thread";
import {
  createChatSession,
  mapApiCitations,
  sendSessionMessage,
} from "@/lib/api/chat";
import {
  getStoredMessages,
  getStoredSessionId,
  setStoredMessages,
  setStoredSessionId,
} from "@/lib/chat-storage";
import { getErrorMessage } from "@/lib/errors";
import { useActiveWorkspace } from "@/hooks/use-active-workspace";

function createMessageId(): string {
  return crypto.randomUUID();
}

export function useChatSession() {
  const { activeWorkspaceId } = useActiveWorkspace();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isInitializing, setIsInitializing] = useState(true);
  const [initError, setInitError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  useEffect(() => {
    let cancelled = false;

    async function initializeSession() {
      if (!activeWorkspaceId) {
        setIsInitializing(false);
        return;
      }

      setIsInitializing(true);
      setInitError(null);

      try {
        const existingSessionId = getStoredSessionId(activeWorkspaceId);
        if (existingSessionId) {
          if (!cancelled) {
            setSessionId(existingSessionId);
            setMessages(getStoredMessages(existingSessionId));
            setIsInitializing(false);
          }
          return;
        }

        const response = await createChatSession({
          workspace_id: activeWorkspaceId,
          title: "Workspace chat",
        });

        if (cancelled) {
          return;
        }

        setStoredSessionId(activeWorkspaceId, response.session_id);
        setSessionId(response.session_id);
        setMessages([]);
        setIsInitializing(false);
      } catch (error) {
        if (!cancelled) {
          setInitError(getErrorMessage(error, "Unable to start chat session."));
          setIsInitializing(false);
        }
      }
    }

    void initializeSession();

    return () => {
      cancelled = true;
    };
  }, [activeWorkspaceId]);

  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      if (!sessionId) {
        throw new Error("Chat session is not ready");
      }
      return sendSessionMessage(sessionId, { message });
    },
    onSuccess: (response) => {
      setMessages((current) => {
        const nextMessages: ChatMessage[] = [
          ...current,
          {
            id: createMessageId(),
            role: "assistant",
            content: response.answer,
            citations: mapApiCitations(response.citations),
          },
        ];
        if (sessionId) {
          setStoredMessages(
            sessionId,
            nextMessages.map((item) => ({
              id: item.id,
              role: item.role,
              content: item.content,
              citations: item.citations?.map((citation) => ({
                id: citation.id,
                documentTitle: citation.documentTitle,
                filePath: citation.filePath,
                repositoryName: citation.repositoryName,
              })),
            })),
          );
        }
        return nextMessages;
      });
      queryClient.invalidateQueries({ queryKey: ["dashboard", "summary"] });
    },
  });

  const sendMessage = useCallback(
    async (message: string) => {
      const trimmed = message.trim();
      if (!trimmed || !sessionId) {
        return;
      }

      setMessages((current) => [
        ...current,
        {
          id: createMessageId(),
          role: "user",
          content: trimmed,
        },
      ]);

      try {
        await sendMessageMutation.mutateAsync(trimmed);
      } catch {
        setMessages((current) => current.slice(0, -1));
      }
    },
    [sendMessageMutation, sessionId],
  );

  const startNewSession = useCallback(async () => {
    if (!activeWorkspaceId) {
      return;
    }

    setIsInitializing(true);
    setInitError(null);

    try {
      const response = await createChatSession({
        workspace_id: activeWorkspaceId,
        title: "Workspace chat",
      });
      setStoredSessionId(activeWorkspaceId, response.session_id);
      setStoredMessages(response.session_id, []);
      setSessionId(response.session_id);
      setMessages([]);
    } catch (error) {
      setInitError(getErrorMessage(error, "Unable to start a new chat session."));
    } finally {
      setIsInitializing(false);
    }
  }, [activeWorkspaceId]);

  return {
    sessionId,
    messages,
    isInitializing,
    initError,
    isSending: sendMessageMutation.isPending,
    sendError: sendMessageMutation.error,
    sendMessage,
    startNewSession,
  };
}
