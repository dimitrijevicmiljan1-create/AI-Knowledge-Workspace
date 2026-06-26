import { routes } from "@/lib/routes";

const DEFAULT_CHAT_TITLE = "New chat";

export function deriveChatTitle(message: string): string {
  const line = message.trim().split(/\r?\n/)[0] ?? "";
  const title = line.slice(0, 80).trim();
  return title || DEFAULT_CHAT_TITLE;
}

export function getBackFallbackPath(pathname: string): string {
  if (pathname.startsWith(`${routes.chat}/`) && pathname !== routes.chatNew) {
    return routes.chatNew;
  }
  if (
    pathname === routes.documents ||
    pathname === routes.sources ||
    pathname === routes.settings
  ) {
    return routes.chatNew;
  }
  return routes.chatNew;
}

export function shouldShowBackButton(pathname: string): boolean {
  if (pathname === routes.chat || pathname === routes.chatNew) {
    return false;
  }
  return (
    pathname.startsWith(`${routes.chat}/`) ||
    pathname === routes.documents ||
    pathname === routes.sources ||
    pathname === routes.settings
  );
}
