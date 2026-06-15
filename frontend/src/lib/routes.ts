export const routes = {
  home: "/",
  login: "/login",
  signup: "/signup",
  chat: "/chat",
  documents: "/documents",
  sources: "/sources",
  settings: "/settings",
  // Legacy routes kept for redirects.
  onboarding: "/chat",
  dashboard: "/chat",
  github: "/sources",
  obsidian: "/sources",
} as const;

export function getPostAuthPath(): string {
  return routes.chat;
}

export const knowledgeNavigation = [
  { name: "Documents", href: routes.documents },
  { name: "Sources", href: routes.sources },
] as const;
