"use client";

import { motion } from "framer-motion";
import {
  LayoutDashboard,
  MessageSquare,
  FolderGit2,
  BookMarked,
  Settings,
  Search,
} from "lucide-react";

import { cardRevealVariants, heroVariants, transitionDefault } from "@/lib/motion";
import { appNavigation } from "@/lib/routes";
import { cn } from "@/lib/utils";

const iconMap = {
  Workspace: LayoutDashboard,
  Chat: MessageSquare,
  Sources: FolderGit2,
  GitHub: FolderGit2,
  Obsidian: BookMarked,
  Settings: Settings,
} as const;

export function ProductPreview() {
  return (
    <section
      className="px-4 py-12 sm:px-6 sm:py-16"
      aria-labelledby="preview-heading"
    >
      <div className="mx-auto max-w-7xl">
        <motion.div
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          variants={heroVariants}
          transition={transitionDefault}
          className="mb-8 text-center"
        >
          <h2 id="preview-heading" className="text-section-title">
            A workspace designed for focus
          </h2>
          <p className="mt-2 text-body text-text-secondary">
            The same application shell you use in production — sidebar, header,
            and content area.
          </p>
        </motion.div>

        <motion.div
          variants={cardRevealVariants}
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          className="overflow-hidden rounded-2xl border border-border bg-surface shadow-[0_24px_80px_rgba(0,0,0,0.45)]"
        >
          <div className="flex border-b border-border bg-background px-4 py-3">
            <div className="flex gap-1.5" aria-hidden="true">
              <span className="size-3 rounded-full bg-border" />
              <span className="size-3 rounded-full bg-border" />
              <span className="size-3 rounded-full bg-border" />
            </div>
          </div>
          <div className="flex min-h-[420px]">
            <aside className="hidden w-56 shrink-0 border-r border-border bg-sidebar p-3 sm:block">
              <div className="mb-4 flex items-center gap-2 px-2">
                <span className="flex size-7 items-center justify-center rounded-md bg-primary text-xs font-bold text-primary-foreground">
                  AI
                </span>
                <span className="text-sm font-semibold">Knowledge</span>
              </div>
              <nav className="space-y-1" aria-label="Preview navigation">
                {appNavigation.map((item) => {
                  const Icon = iconMap[item.name as keyof typeof iconMap];
                  const active = item.name === "Workspace";
                  return (
                    <div
                      key={item.href}
                      className={cn(
                        "flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm",
                        active
                          ? "bg-primary/15 text-primary"
                          : "text-text-secondary",
                      )}
                    >
                      <Icon className="size-4 shrink-0" aria-hidden="true" />
                      {item.name}
                    </div>
                  );
                })}
              </nav>
            </aside>
            <div className="flex min-w-0 flex-1 flex-col">
              <header className="flex h-14 items-center justify-between border-b border-border px-4">
                <div className="text-sm font-medium">Workspace</div>
                <div className="hidden max-w-xs flex-1 px-6 md:block">
                  <div className="flex h-8 items-center gap-2 rounded-lg border border-border bg-elevated px-3 text-meta">
                    <Search className="size-3.5" aria-hidden="true" />
                    Search knowledge…
                  </div>
                </div>
                <div className="size-8 rounded-full bg-elevated" aria-hidden="true" />
              </header>
              <div className="flex flex-1 flex-col gap-4 p-4 md:p-6">
                <div className="grid gap-3 sm:grid-cols-3">
                  {["Workspaces", "Documents", "Conversations"].map((label) => (
                    <div
                      key={label}
                      className="rounded-xl border border-border bg-elevated p-4"
                    >
                      <p className="text-meta">{label}</p>
                      <div className="mt-2 h-7 w-12 rounded-md bg-surface" />
                    </div>
                  ))}
                </div>
                <div className="flex flex-1 items-center justify-center rounded-xl border border-dashed border-border bg-elevated/50 p-8 text-center">
                  <p className="max-w-sm text-sm text-text-secondary">
                    Your dashboard, sources, and chat live here — connected to
                    real backend data.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
