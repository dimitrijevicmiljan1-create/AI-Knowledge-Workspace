"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useCreateChat } from "@/hooks/use-chats";
import { routes } from "@/lib/routes";
import { Skeleton } from "@/components/ui/skeleton";

export default function NewChatPage() {
  const router = useRouter();
  const createChat = useCreateChat();

  useEffect(() => {
    let cancelled = false;

    async function startChat() {
      try {
        const chat = await createChat.mutateAsync(undefined);
        if (!cancelled) {
          router.replace(`${routes.chat}/${chat.id}`);
        }
      } catch {
        if (!cancelled) {
          router.replace(routes.chat);
        }
      }
    }

    void startChat();

    return () => {
      cancelled = true;
    };
  }, [createChat, router]);

  return (
    <div className="flex h-[calc(100vh-4rem)] items-center justify-center">
      <Skeleton className="h-8 w-48" />
    </div>
  );
}
