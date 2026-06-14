import { BookMarked, Link2, Search, Sparkles } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";

const features = [
  {
    icon: Link2,
    title: "Vault connection",
    description:
      "Connect Obsidian vaults to sync notes and markdown files into your workspace.",
  },
  {
    icon: Search,
    title: "Semantic search",
    description:
      "Search across linked notes with the same vector retrieval used for chat.",
  },
  {
    icon: Sparkles,
    title: "Chat with notes",
    description:
      "Ask questions grounded in your vault content with citation-backed answers.",
  },
];

export function ObsidianComingSoon() {
  return (
    <div className="space-y-6">
      <Card className="overflow-hidden">
        <CardHeader className="border-b border-border bg-surface/50">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex size-12 items-center justify-center rounded-xl bg-[#7C3AED]/15">
                <BookMarked className="size-6 text-[#A78BFA]" aria-hidden="true" />
              </div>
              <div>
                <CardTitle>Obsidian integration</CardTitle>
                <CardDescription>
                  Bring your personal knowledge base into the workspace.
                </CardDescription>
              </div>
            </div>
            <StatusBadge label="Coming soon" variant="info" />
          </div>
        </CardHeader>
        <CardContent className="space-y-6 pt-6">
          <p className="max-w-3xl text-sm text-text-secondary">
            Obsidian vault syncing is planned for a future release. The backend
            connector is not available yet, so this page provides an overview of
            the upcoming workflow without enabling plugin functionality.
          </p>

          <div className="grid gap-4 md:grid-cols-3">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <div
                  key={feature.title}
                  className="rounded-xl border border-border bg-surface p-4"
                >
                  <div className="mb-3 flex size-10 items-center justify-center rounded-lg bg-elevated">
                    <Icon className="size-5 text-primary" aria-hidden="true" />
                  </div>
                  <h3 className="text-sm font-semibold">{feature.title}</h3>
                  <p className="mt-1 text-sm text-text-secondary">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
