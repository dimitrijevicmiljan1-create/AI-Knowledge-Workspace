"use client";

import { use } from "react";

import { ChatPageContent } from "@/components/chat/chat-page-content";

export default function ChatDetailPage({
  params,
}: {
  params: Promise<{ chatId: string }>;
}) {
  const { chatId } = use(params);
  return <ChatPageContent chatId={chatId} />;
}
