import { apiRequest } from "@/lib/api/client";
import type {
  IntegrationStatus,
  UsageStats,
  UserSettings,
} from "@/lib/api/types";
import type { User } from "@/lib/api/types";

export type UpdateUserSettingsPayload = Partial<
  Pick<
    UserSettings,
    | "default_model"
    | "temperature"
    | "response_length"
    | "chunk_size"
    | "chunk_overlap"
    | "auto_index_uploads"
  >
>;

export async function getAiSettings(): Promise<UserSettings> {
  return apiRequest<UserSettings>("/settings/ai");
}

export async function updateAiSettings(
  payload: UpdateUserSettingsPayload,
): Promise<UserSettings> {
  return apiRequest<UserSettings>("/settings/ai", {
    method: "PATCH",
    body: payload,
  });
}

export async function getKnowledgeSettings(): Promise<UserSettings> {
  return apiRequest<UserSettings>("/settings/knowledge");
}

export async function updateKnowledgeSettings(
  payload: UpdateUserSettingsPayload,
): Promise<UserSettings> {
  return apiRequest<UserSettings>("/settings/knowledge", {
    method: "PATCH",
    body: payload,
  });
}

export async function getIntegrations(): Promise<IntegrationStatus> {
  return apiRequest<IntegrationStatus>("/settings/integrations");
}

export async function getUsageStats(): Promise<UsageStats> {
  return apiRequest<UsageStats>("/settings/usage");
}

export type UpdateProfilePayload = {
  email?: string;
  full_name?: string;
  password?: string;
};

export async function updateProfile(
  payload: UpdateProfilePayload,
): Promise<User> {
  return apiRequest<User>("/users/me", {
    method: "PATCH",
    body: payload,
  });
}
