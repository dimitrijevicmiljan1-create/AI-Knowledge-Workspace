"use client";

import { ChatComposer } from "@/components/chat/chat-composer";
import { ChatThread } from "@/components/chat/chat-thread";
import { NoChatsEmptyState } from "@/components/empty-states";
import { PageHeader } from "@/components/layout/page-header";

export default function ChatPage() {
  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col overflow-hidden rounded-2xl border border-border bg-surface">
      <PageHeader
        title="Chat"
        description="Ask questions about your knowledge base. Streaming will be enabled in a future release."
        className="border-b border-border px-4 py-4 sm:px-6"
      />
      <ChatThread messages={[]} emptyState={<NoChatsEmptyState />} />
      <ChatComposer disabled />
    </div>
  );
}
