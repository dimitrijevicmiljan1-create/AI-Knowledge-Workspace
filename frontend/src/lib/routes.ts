export const routes = {
  home: "/",
  login: "/login",
  signup: "/signup",
  chat: "/chat",
  chatNew: "/chat/new",
  documents: "/documents",
  sources: "/sources",
  settings: "/settings",
  // Legacy routes kept for redirects.
  onboarding: "/chat/new",
  dashboard: "/chat/new",
  github: "/sources",
  obsidian: "/sources",
} as const;

export const knowledgeNavigation = [
  { name: "Documents", href: routes.documents },
  { name: "Integrations", href: routes.sources },
] as const;
