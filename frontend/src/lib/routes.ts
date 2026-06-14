export const routes = {
  home: "/",
  login: "/login",
  signup: "/signup",
  onboarding: "/onboarding",
  dashboard: "/dashboard",
} as const;

export async function getPostAuthPath(
  workspaceCount: number,
): Promise<string> {
  return workspaceCount === 0 ? routes.onboarding : routes.dashboard;
}
