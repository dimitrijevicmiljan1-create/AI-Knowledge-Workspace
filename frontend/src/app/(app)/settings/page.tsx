"use client";

import { Settings } from "lucide-react";
import { useState } from "react";

import { ErrorBanner } from "@/components/ui/error-banner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/ui/empty-state";
import { useAuth } from "@/hooks/use-auth";
import {
  getAiSettings,
  getIntegrations,
  getKnowledgeSettings,
  getUsageStats,
  updateAiSettings,
  updateKnowledgeSettings,
  updateProfile,
} from "@/lib/api/settings";
import { getErrorMessage } from "@/lib/errors";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useConnectGitHub } from "@/hooks/use-github";
import { routes } from "@/lib/routes";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function SettingsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const connectGitHub = useConnectGitHub();

  const aiQuery = useQuery({ queryKey: ["settings", "ai"], queryFn: getAiSettings });
  const knowledgeQuery = useQuery({
    queryKey: ["settings", "knowledge"],
    queryFn: getKnowledgeSettings,
  });
  const integrationsQuery = useQuery({
    queryKey: ["settings", "integrations"],
    queryFn: getIntegrations,
  });
  const usageQuery = useQuery({
    queryKey: ["settings", "usage"],
    queryFn: getUsageStats,
  });

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [profileError, setProfileError] = useState<string | null>(null);
  const [settingsError, setSettingsError] = useState<string | null>(null);

  const profileMutation = useMutation({
    mutationFn: updateProfile,
    onSuccess: () => {
      setPassword("");
      setProfileError(null);
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    },
    onError: (error) => {
      setProfileError(getErrorMessage(error));
    },
  });

  const aiMutation = useMutation({
    mutationFn: updateAiSettings,
    onSuccess: () => {
      setSettingsError(null);
      queryClient.invalidateQueries({ queryKey: ["settings", "ai"] });
    },
    onError: (error) => setSettingsError(getErrorMessage(error)),
  });

  const knowledgeMutation = useMutation({
    mutationFn: updateKnowledgeSettings,
    onSuccess: () => {
      setSettingsError(null);
      queryClient.invalidateQueries({ queryKey: ["settings", "knowledge"] });
    },
    onError: (error) => setSettingsError(getErrorMessage(error)),
  });

  if (!user) {
    return (
      <section className="space-y-6">
        <PageHeader title="Settings" description="Manage your account and preferences." />
        <EmptyState
          icon={<Settings className="size-6 text-muted-foreground" aria-hidden="true" />}
          title="Settings unavailable"
          description="Sign in to manage your account settings."
          actionLabel="Sign in"
          actionHref={routes.login}
        />
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-4xl space-y-6">
      <PageHeader
        title="Settings"
        description="Manage your profile, AI preferences, knowledge settings, and integrations."
      />

      {settingsError ? <ErrorBanner message={settingsError} /> : null}

      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
          <CardDescription>Update your account information.</CardDescription>
        </CardHeader>
        <CardContent>
          <form
            className="space-y-4"
            onSubmit={(event) => {
              event.preventDefault();
              profileMutation.mutate({
                full_name: fullName || user.full_name || undefined,
                email: email || user.email,
                password: password || undefined,
              });
            }}
          >
            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="full-name">
                Name
              </label>
              <Input
                id="full-name"
                defaultValue={user.full_name ?? ""}
                onChange={(event) => setFullName(event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="email">
                Email
              </label>
              <Input
                id="email"
                type="email"
                defaultValue={user.email}
                onChange={(event) => setEmail(event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="password">
                Password
              </label>
              <Input
                id="password"
                type="password"
                placeholder="Leave blank to keep current password"
                onChange={(event) => setPassword(event.target.value)}
              />
            </div>
            {profileError ? <ErrorBanner message={profileError} /> : null}
            <Button type="submit" disabled={profileMutation.isPending}>
              Save profile
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>AI settings</CardTitle>
          <CardDescription>Configure default model behavior for chat.</CardDescription>
        </CardHeader>
        <CardContent>
          {aiQuery.isLoading || !aiQuery.data ? (
            <Skeleton className="h-24 w-full" />
          ) : (
            <form
              className="grid gap-4 sm:grid-cols-2"
              onSubmit={(event) => {
                event.preventDefault();
                const formData = new FormData(event.currentTarget);
                aiMutation.mutate({
                  default_model: String(formData.get("default_model")),
                  temperature: Number(formData.get("temperature")),
                  response_length: String(formData.get("response_length")),
                });
              }}
            >
              <div className="space-y-2">
                <label className="text-sm font-medium" htmlFor="default_model">
                  Default model
                </label>
                <Input
                  id="default_model"
                  name="default_model"
                  defaultValue={aiQuery.data.default_model}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium" htmlFor="temperature">
                  Temperature
                </label>
                <Input
                  id="temperature"
                  name="temperature"
                  type="number"
                  step="0.1"
                  min="0"
                  max="2"
                  defaultValue={aiQuery.data.temperature}
                />
              </div>
              <div className="space-y-2 sm:col-span-2">
                <label className="text-sm font-medium" htmlFor="response_length">
                  Response length
                </label>
                <select
                  id="response_length"
                  name="response_length"
                  defaultValue={aiQuery.data.response_length}
                  className="h-10 w-full rounded-lg border border-border bg-surface px-3 text-sm"
                >
                  <option value="short">Short</option>
                  <option value="medium">Medium</option>
                  <option value="long">Long</option>
                </select>
              </div>
              <Button type="submit" disabled={aiMutation.isPending}>
                Save AI settings
              </Button>
            </form>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Knowledge settings</CardTitle>
          <CardDescription>Control indexing and chunking defaults.</CardDescription>
        </CardHeader>
        <CardContent>
          {knowledgeQuery.isLoading || !knowledgeQuery.data ? (
            <Skeleton className="h-24 w-full" />
          ) : (
            <form
              className="grid gap-4 sm:grid-cols-2"
              onSubmit={(event) => {
                event.preventDefault();
                const formData = new FormData(event.currentTarget);
                knowledgeMutation.mutate({
                  chunk_size: Number(formData.get("chunk_size")),
                  chunk_overlap: Number(formData.get("chunk_overlap")),
                  auto_index_uploads: formData.get("auto_index_uploads") === "on",
                });
              }}
            >
              <div className="space-y-2">
                <label className="text-sm font-medium" htmlFor="chunk_size">
                  Chunk size
                </label>
                <Input
                  id="chunk_size"
                  name="chunk_size"
                  type="number"
                  defaultValue={knowledgeQuery.data.chunk_size}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium" htmlFor="chunk_overlap">
                  Chunk overlap
                </label>
                <Input
                  id="chunk_overlap"
                  name="chunk_overlap"
                  type="number"
                  defaultValue={knowledgeQuery.data.chunk_overlap}
                />
              </div>
              <label className="flex items-center gap-2 text-sm sm:col-span-2">
                <input
                  type="checkbox"
                  name="auto_index_uploads"
                  defaultChecked={knowledgeQuery.data.auto_index_uploads}
                />
                Auto-index uploads
              </label>
              <Button type="submit" disabled={knowledgeMutation.isPending}>
                Save knowledge settings
              </Button>
            </form>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Integrations</CardTitle>
          <CardDescription>Connect external knowledge sources.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {integrationsQuery.isLoading ? (
            <Skeleton className="h-20 w-full" />
          ) : (
            <>
              <div className="flex items-center justify-between rounded-xl border border-border bg-surface p-4">
                <div>
                  <p className="text-sm font-medium">GitHub</p>
                  <p className="text-meta">
                    {integrationsQuery.data?.github_connected
                      ? `Connected as @${integrationsQuery.data.github_username}`
                      : "Not connected"}
                  </p>
                </div>
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => connectGitHub.mutate()}
                  disabled={connectGitHub.isPending}
                >
                  {integrationsQuery.data?.github_connected ? "Reconnect" : "Connect"}
                </Button>
              </div>
              <div className="flex items-center justify-between rounded-xl border border-border bg-surface p-4 opacity-70">
                <div>
                  <p className="text-sm font-medium">Notion</p>
                  <p className="text-meta">Coming soon</p>
                </div>
              </div>
              <div className="flex items-center justify-between rounded-xl border border-border bg-surface p-4 opacity-70">
                <div>
                  <p className="text-sm font-medium">Google Drive</p>
                  <p className="text-meta">Coming soon</p>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Usage</CardTitle>
          <CardDescription>Workspace consumption overview.</CardDescription>
        </CardHeader>
        <CardContent>
          {usageQuery.isLoading || !usageQuery.data ? (
            <Skeleton className="h-20 w-full" />
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-xl border border-border bg-surface p-4">
                <p className="text-meta">Documents</p>
                <p className="text-lg font-semibold">{usageQuery.data.documents}</p>
              </div>
              <div className="rounded-xl border border-border bg-surface p-4">
                <p className="text-meta">Chunks</p>
                <p className="text-lg font-semibold">{usageQuery.data.chunks}</p>
              </div>
              <div className="rounded-xl border border-border bg-surface p-4">
                <p className="text-meta">Storage</p>
                <p className="text-lg font-semibold">
                  {formatBytes(usageQuery.data.storage_bytes)}
                </p>
              </div>
              <div className="rounded-xl border border-border bg-surface p-4">
                <p className="text-meta">Queries</p>
                <p className="text-lg font-semibold">{usageQuery.data.queries}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </section>
  );
}
