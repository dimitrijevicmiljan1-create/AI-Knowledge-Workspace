import { apiRequest } from "@/lib/api/client";
import type { TokenResponse, User } from "@/lib/api/types";
import { clearTokens, setTokens } from "@/lib/auth-storage";
import { clearLastChatId } from "@/lib/chat-storage";

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = {
  email: string;
  password: string;
  full_name?: string;
};

export async function loginUser(payload: LoginPayload): Promise<User> {
  const tokens = await apiRequest<TokenResponse>("/auth/login", {
    method: "POST",
    body: payload,
    auth: false,
  });
  setTokens(tokens.access_token, tokens.refresh_token);
  return getCurrentUser();
}

export async function registerUser(payload: RegisterPayload): Promise<User> {
  return apiRequest<User>("/auth/register", {
    method: "POST",
    body: payload,
    auth: false,
  });
}

export async function getCurrentUser(): Promise<User> {
  return apiRequest<User>("/auth/me");
}

export function logoutUser(): void {
  clearTokens();
  clearLastChatId();
}
