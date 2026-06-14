"use client";

import { Settings } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";
import { PageHeader } from "@/components/layout/page-header";
import { useAuth } from "@/hooks/use-auth";

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <section className="space-y-6">
      <PageHeader
        title="Settings"
        description="Manage your account and workspace preferences."
      />
      {user ? (
        <div className="surface-panel max-w-lg space-y-4 p-6">
          <div>
            <p className="text-meta">Account</p>
            <p className="mt-1 font-medium">{user.full_name ?? user.email}</p>
            {user.full_name ? (
              <p className="text-sm text-text-secondary">{user.email}</p>
            ) : null}
          </div>
        </div>
      ) : (
        <EmptyState
          icon={<Settings className="size-6 text-muted-foreground" aria-hidden="true" />}
          title="Settings unavailable"
          description="Sign in to manage your account settings."
          actionLabel="Sign in"
          actionHref="/login"
        />
      )}
    </section>
  );
}
