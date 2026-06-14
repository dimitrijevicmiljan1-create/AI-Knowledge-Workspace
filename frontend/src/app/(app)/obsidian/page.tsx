"use client";

import { ObsidianComingSoon } from "@/components/obsidian/obsidian-coming-soon";
import { PageHeader } from "@/components/layout/page-header";

export default function ObsidianPage() {
  return (
    <section className="space-y-6">
      <PageHeader
        title="Obsidian"
        description="Connect vaults to search and chat with your notes."
      />
      <ObsidianComingSoon />
    </section>
  );
}
