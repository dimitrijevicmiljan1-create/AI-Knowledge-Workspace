export const routes = {
  home: "/",
  login: "/login",
  signup: "/signup",
  onboarding: "/onboarding",
  dashboard: "/dashboard",
  chat: "/chat",
  sources: "/sources",
  github: "/github",
  obsidian: "/obsidian",
  settings: "/settings",
} as const;

export async function getPostAuthPath(
  workspaceCount: number,
): Promise<string> {
  return workspaceCount === 0 ? routes.onboarding : routes.dashboard;
}

export const appNavigation = [
  { name: "Workspace", href: routes.dashboard, section: "workspace" as const },
  { name: "Chat", href: routes.chat, section: "chat" as const },
  { name: "Sources", href: routes.sources, section: "sources" as const },
  { name: "GitHub", href: routes.github, section: "github" as const },
  { name: "Obsidian", href: routes.obsidian, section: "obsidian" as const },
  { name: "Settings", href: routes.settings, section: "settings" as const },
] as const;
