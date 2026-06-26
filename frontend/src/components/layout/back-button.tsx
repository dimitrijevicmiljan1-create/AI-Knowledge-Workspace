"use client";

import { ArrowLeft } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { useChats } from "@/hooks/use-chats";
import { resolveChatHomePath } from "@/lib/chat-navigation";
import {
  getBackFallbackPath,
  shouldShowBackButton,
} from "@/lib/navigation";

export function BackButton() {
  const router = useRouter();
  const pathname = usePathname();
  const { data: chats } = useChats();

  if (!shouldShowBackButton(pathname)) {
    return null;
  }

  const fallbackHref =
    pathname.startsWith("/chat/") && pathname !== "/chat/new"
      ? resolveChatHomePath(chats)
      : getBackFallbackPath(pathname);

  function handleBack() {
    if (typeof window !== "undefined" && window.history.length > 1) {
      router.back();
      return;
    }
    router.push(fallbackHref);
  }

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon-sm"
      onClick={handleBack}
      aria-label="Go back"
      title="Go back"
      className="text-text-secondary"
    >
      <ArrowLeft className="size-4" />
    </Button>
  );
}
