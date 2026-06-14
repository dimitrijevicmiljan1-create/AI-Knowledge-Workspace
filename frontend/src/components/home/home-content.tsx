"use client";

import Link from "next/link";
import { FolderOpen, LogIn } from "lucide-react";

import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/use-auth";
import { useWorkspaces } from "@/hooks/use-workspaces";
import { hasStoredSession } from "@/lib/auth-storage";

export function HomeContent() {
  const { isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const {
    data: workspaces,
    isLoading: isWorkspacesLoading,
    isError,
    error,
  } = useWorkspaces(isAuthenticated);

  if (!hasStoredSession()) {
    return (
      <EmptyState
        icon={<LogIn className="size-6 text-muted-foreground" />}
        title="Sign in to get started"
        description="Create an account or sign in to access your workspaces and knowledge sources."
        actionLabel="Sign in"
        onAction={() => {
          window.location.href = "/login";
        }}
      />
    );
  }

  if (isAuthLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-96" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <EmptyState
        icon={<LogIn className="size-6 text-muted-foreground" />}
        title="Session expired"
        description="Your session is no longer valid. Sign in again to continue."
        actionLabel="Sign in"
        onAction={() => {
          window.location.href = "/login";
        }}
      />
    );
  }

  if (isWorkspacesLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-4 sm:grid-cols-2">
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <EmptyState
        icon={<FolderOpen className="size-6 text-muted-foreground" />}
        title="Unable to load workspaces"
        description={
          error instanceof Error
            ? error.message
            : "Something went wrong while fetching your workspaces."
        }
      />
    );
  }

  if (!workspaces || workspaces.items.length === 0) {
    return (
      <EmptyState
        icon={<FolderOpen className="size-6 text-muted-foreground" />}
        title="No workspaces yet"
        description="Create your first workspace to start organizing documents, sources, and conversations."
      />
    );
  }

  return (
    <section className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">Workspaces</h2>
        <p className="text-text-secondary">
          {workspaces.total} workspace{workspaces.total === 1 ? "" : "s"}
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {workspaces.items.map((workspace) => (
          <Link key={workspace.id} href={`/dashboard`}>
            <Card className="h-full transition-colors hover:border-primary/40">
              <CardHeader>
                <CardTitle>{workspace.name}</CardTitle>
                <CardDescription>
                  {workspace.description ?? "No description"}
                </CardDescription>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </section>
  );
}
