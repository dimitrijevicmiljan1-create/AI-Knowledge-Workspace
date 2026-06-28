"use client";

import { useState } from "react";

import { GitHubIntegrationPanel } from "@/components/integrations/github-integration-panel";
import { IntegrationCard } from "@/components/integrations/integration-card";
import { IntegrationSection } from "@/components/integrations/integration-section";
import { LocalDocumentsIntegrationPanel } from "@/components/integrations/local-documents-integration-panel";
import { PageHeader } from "@/components/layout/page-header";
import { Skeleton } from "@/components/ui/skeleton";
import {
  integrationCategories,
  knowledgeComingSoonIntegrations,
} from "@/lib/integrations/catalog";
import { useUserWorkspace } from "@/hooks/use-user-workspace";

type ExpandedIntegration = "github" | "local-documents" | null;

export default function IntegrationsPage() {
  const { isLoading: isWorkspaceLoading } = useUserWorkspace();
  const [expandedIntegration, setExpandedIntegration] =
    useState<ExpandedIntegration>(null);

  function toggleIntegration(id: ExpandedIntegration) {
    setExpandedIntegration((current) => (current === id ? null : id));
  }

  if (isWorkspaceLoading) {
    return (
      <section className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-40 w-full" />
      </section>
    );
  }

  return (
    <section className="mx-auto max-w-7xl space-y-8">
      <PageHeader
        title="Integrations"
        description="Connect knowledge sources and services to your personal workspace."
      />

      <IntegrationSection title="Knowledge" emoji="📚">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <GitHubIntegrationPanel
            isExpanded={expandedIntegration === "github"}
            onToggle={() => toggleIntegration("github")}
          />

          <LocalDocumentsIntegrationPanel
            isExpanded={expandedIntegration === "local-documents"}
            onToggle={() => toggleIntegration("local-documents")}
          />

          {knowledgeComingSoonIntegrations.map((integration) => (
            <IntegrationCard
              key={integration.id}
              name={integration.name}
              description={integration.description}
              icon={integration.icon}
              status={integration.status}
              connectLabel="Connect"
            />
          ))}
        </div>
      </IntegrationSection>

      {integrationCategories.map((category) => (
        <IntegrationSection
          key={category.id}
          title={category.title}
          emoji={category.emoji}
        >
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {category.integrations.map((integration) => (
              <IntegrationCard
                key={integration.id}
                name={integration.name}
                description={integration.description}
                icon={integration.icon}
                status={integration.status}
                connectLabel="Connect"
              />
            ))}
          </div>
        </IntegrationSection>
      ))}
    </section>
  );
}
