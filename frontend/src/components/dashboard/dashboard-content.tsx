"use client";

import { LayoutDashboard, LogIn } from "lucide-react";

import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/use-auth";
import { useDashboardSummary } from "@/hooks/use-workspaces";
import { hasStoredSession } from "@/lib/auth-storage";

function StatCard({
  label,
  value,
  isLoading,
}: {
  label: string;
  value: number;
  isLoading: boolean;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-3xl font-bold">
          {isLoading ? <Skeleton className="h-9 w-12" /> : value}
        </CardTitle>
      </CardHeader>
    </Card>
  );
}

export function DashboardContent() {
  const { isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const {
    data: summary,
    isLoading: isSummaryLoading,
    isError,
    error,
  } = useDashboardSummary(isAuthenticated);

  if (!hasStoredSession()) {
    return (
      <EmptyState
        icon={<LogIn className="size-6 text-muted-foreground" />}
        title="Sign in required"
        description="Sign in to view your dashboard and workspace statistics."
        actionLabel="Sign in"
        onAction={() => {
          window.location.href = "/login";
        }}
      />
    );
  }

  if (isAuthLoading) {
    return (
      <div className="space-y-8">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-4 sm:grid-cols-3">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <EmptyState
        icon={<LogIn className="size-6 text-muted-foreground" />}
        title="Session expired"
        description="Your session is no longer valid. Sign in again to view your dashboard."
        actionLabel="Sign in"
        onAction={() => {
          window.location.href = "/login";
        }}
      />
    );
  }

  if (isError) {
    return (
      <EmptyState
        icon={<LayoutDashboard className="size-6 text-muted-foreground" />}
        title="Unable to load dashboard"
        description={
          error instanceof Error
            ? error.message
            : "Something went wrong while fetching your statistics."
        }
      />
    );
  }

  const isLoading = isSummaryLoading || !summary;
  const hasNoData =
    summary &&
    summary.workspaceCount === 0 &&
    summary.documentCount === 0 &&
    summary.conversationCount === 0;

  return (
    <section className="mx-auto max-w-7xl space-y-8">
      <div className="space-y-2">
        <h2 className="text-page-title">Dashboard</h2>
        <p className="text-text-secondary">
          Overview of your workspaces, documents, and conversations.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          label="Workspaces"
          value={summary?.workspaceCount ?? 0}
          isLoading={isLoading}
        />
        <StatCard
          label="Documents"
          value={summary?.documentCount ?? 0}
          isLoading={isLoading}
        />
        <StatCard
          label="Conversations"
          value={summary?.conversationCount ?? 0}
          isLoading={isLoading}
        />
      </div>

      {hasNoData ? (
        <EmptyState
          icon={<LayoutDashboard className="size-6 text-muted-foreground" />}
          title="No data yet"
          description="Create a workspace to start adding documents and conversations. Your statistics will appear here once you have content."
        />
      ) : null}
    </section>
  );
}
