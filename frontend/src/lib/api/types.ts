export type User = {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
};

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type Workspace = {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  created_at: string;
  updated_at: string;
};

export type WorkspaceListResponse = {
  items: Workspace[];
  total: number;
};

export type WorkspaceStats = {
  workspace_id: string;
  document_count: number;
  source_count: number;
  chat_count: number;
  created_at: string;
};

export type ApiErrorBody = {
  detail?: string | { msg: string }[];
};
