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
  detail?: string | { msg: string }[] | { message?: string; errors?: { field: string; message: string }[] };
};

export type UploadStatus = "created" | "skipped" | "failed";

export type FileUploadResult = {
  filename: string;
  status: UploadStatus;
  document_id: string | null;
  size: number | null;
  checksum: string | null;
  message: string | null;
  errors: Array<{ field: string; message: string }>;
};

export type FileUploadResponse = {
  file: FileUploadResult;
};

export type MultipleFileUploadResponse = {
  uploaded: number;
  skipped: number;
  failed: number;
  results: FileUploadResult[];
};

export type WorkspaceFile = {
  document_id: string;
  filename: string;
  size: number;
  uploaded_at: string;
};

export type WorkspaceFileListResponse = {
  items: WorkspaceFile[];
  total: number;
};

export type DocumentStats = {
  document_id: string;
  chunk_count: number;
  indexed_at: string | null;
  checksum: string;
};

export type SourceStatus = "pending" | "ready" | "syncing" | "failed";

export type SourceType = "github" | "obsidian" | "local_files" | "manual";

export type Source = {
  id: string;
  workspace_id: string;
  name: string;
  source_type: SourceType;
  config: Record<string, unknown>;
  status: SourceStatus;
  last_sync_at: string | null;
  created_at: string;
  updated_at: string;
};

export type SourceListResponse = {
  items: Source[];
  total: number;
};

export type SourceStats = {
  source_id: string;
  document_count: number;
  chunk_count: number;
  last_sync_at: string | null;
  status: SourceStatus;
};

export type GitHubConnectResponse = {
  authorization_url: string;
};

export type GitHubConnection = {
  github_username: string;
  connected_at: string;
};

export type GitHubDiscoveredRepository = {
  github_repo_id: number;
  owner: string;
  name: string;
  full_name: string;
  default_branch: string;
  visibility: string;
  description: string | null;
  updated_at: string;
  private: boolean;
};

export type GitHubRepositoryDiscoveryResponse = {
  items: GitHubDiscoveredRepository[];
  page: number;
  per_page: number;
  total: number;
};

export type GitHubRepositorySyncStatus =
  | "pending"
  | "syncing"
  | "ready"
  | "failed";

export type GitHubSyncJobStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed";

export type GitHubRepository = {
  id: string;
  workspace_id: string;
  source_id: string;
  github_repo_id: number;
  repository_owner: string;
  repository_name: string;
  default_branch: string;
  last_commit_sha: string | null;
  last_synced_at: string | null;
  sync_status: GitHubRepositorySyncStatus;
  created_at: string;
  updated_at: string;
};

export type GitHubRepositorySyncResponse = {
  job_id: string;
  repository_id: string;
  status: GitHubSyncJobStatus;
};

export type GitHubSyncJob = {
  id: string;
  repository_id: string;
  status: GitHubSyncJobStatus;
  started_at: string | null;
  completed_at: string | null;
  files_scanned: number;
  documents_created: number;
  documents_updated: number;
  documents_deleted: number;
  error_message: string | null;
  created_at: string;
};

export type ObsidianVaultSyncStatus =
  | "pending"
  | "syncing"
  | "ready"
  | "failed";

export type ObsidianSyncJobStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed";

export type ObsidianVault = {
  id: string;
  workspace_id: string;
  source_id: string;
  vault_name: string;
  last_synced_at: string | null;
  sync_status: ObsidianVaultSyncStatus;
  created_at: string;
  updated_at: string;
};

export type ObsidianVaultListResponse = {
  items: ObsidianVault[];
  total: number;
};

export type ObsidianVaultSyncResponse = {
  job_id: string;
  vault_id: string;
  status: ObsidianSyncJobStatus;
};

export type ObsidianSyncJob = {
  id: string;
  vault_id: string;
  status: ObsidianSyncJobStatus;
  started_at: string | null;
  completed_at: string | null;
  files_scanned: number;
  documents_created: number;
  documents_updated: number;
  documents_deleted: number;
  error_message: string | null;
  created_at: string;
};

export type ApiCitation = {
  chunk_id: string;
  document_id: string;
  source_id: string;
  document_title: string;
  file_path: string | null;
  repository_name: string | null;
  vault_name?: string | null;
  source_type?: string | null;
};

export type ChatSessionCreateResponse = {
  session_id: string;
};

export type ChatSummary = {
  id: string;
  workspace_id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type ChatListResponse = {
  items: ChatSummary[];
  total: number;
};

export type ChatCreateResponse = {
  id: string;
};

export type ChatMessageItem = {
  id: string;
  role: string;
  content: string;
  created_at: string;
};

export type ChatMessageListResponse = {
  items: ChatMessageItem[];
  total: number;
};

export type UserSettings = {
  default_model: string;
  temperature: number;
  response_length: string;
  chunk_size: number;
  chunk_overlap: number;
  auto_index_uploads: boolean;
};

export type IntegrationStatus = {
  github_connected: boolean;
  github_username: string | null;
  notion_connected: boolean;
  google_drive_connected: boolean;
};

export type UsageStats = {
  documents: number;
  chunks: number;
  storage_bytes: number;
  queries: number;
};

export type SessionMessageResponse = {
  answer: string;
  citations: ApiCitation[];
};
