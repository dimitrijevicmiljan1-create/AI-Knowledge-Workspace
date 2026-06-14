"use client";

import { NoGithubEmptyState } from "@/components/empty-states";
import { PageHeader } from "@/components/layout/page-header";

export default function GithubPage() {
  return (
    <section className="space-y-6">
      <PageHeader
        title="GitHub"
        description="Connect repositories to index code and documentation."
      />
      <NoGithubEmptyState />
    </section>
  );
}
