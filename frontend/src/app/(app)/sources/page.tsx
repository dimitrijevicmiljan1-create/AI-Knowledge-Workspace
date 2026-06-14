"use client";

import { NoSourcesEmptyState } from "@/components/empty-states";
import { PageHeader } from "@/components/layout/page-header";

export default function SourcesPage() {
  return (
    <section className="space-y-6">
      <PageHeader
        title="Sources"
        description="Manage documents, GitHub repositories, and Obsidian vaults in your workspace."
      />
      <NoSourcesEmptyState />
    </section>
  );
}
