"use client";

import { useEffect, useRef } from "react";

import { MessageBubble } from "@/components/chat/message-bubble";
import { TypingIndicator } from "@/components/chat/typing-indicator";
import type { Citation } from "@/components/chat/citation-badge";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
};

type ChatThreadProps = {
  messages: ChatMessage[];
  isTyping?: boolean;
  emptyState: React.ReactNode;
};

export function ChatThread({ messages, isTyping = false, emptyState }: ChatThreadProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  if (messages.length === 0 && !isTyping) {
    return <div className="flex flex-1 items-center justify-center p-6">{emptyState}</div>;
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
      <div className="mx-auto flex max-w-3xl flex-col gap-4">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            role={message.role}
            content={message.content}
            citations={message.citations}
          />
        ))}
        {isTyping ? (
          <div className="flex justify-start">
            <TypingIndicator />
          </div>
        ) : null}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
