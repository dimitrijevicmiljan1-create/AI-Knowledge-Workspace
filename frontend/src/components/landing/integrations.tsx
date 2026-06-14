"use client";

import { motion } from "framer-motion";
import { FileText, FolderGit2, Hash, BookMarked } from "lucide-react";

import {
  cardRevealVariants,
  staggerContainerVariants,
} from "@/lib/motion";

const integrations = [
  {
    name: "GitHub",
    description: "Repositories, issues, and markdown files",
    icon: FolderGit2,
  },
  {
    name: "Obsidian",
    description: "Vaults and linked notes",
    icon: BookMarked,
  },
  {
    name: "Documents",
    description: "PDF, DOCX, and plain text uploads",
    icon: FileText,
  },
  {
    name: "Markdown",
    description: "Native support for .md knowledge bases",
    icon: Hash,
  },
];

export function Integrations() {
  return (
    <section
      id="integrations"
      className="border-t border-border/60 px-4 py-20 sm:px-6"
      aria-labelledby="integrations-heading"
    >
      <div className="mx-auto max-w-7xl">
        <div className="mx-auto max-w-2xl text-center">
          <h2
            id="integrations-heading"
            className="text-2xl font-bold tracking-tight sm:text-3xl"
          >
            Connect your sources
          </h2>
          <p className="mt-3 text-text-secondary">
            Unified search and chat across the tools you already use.
          </p>
        </div>

        <motion.div
          initial="initial"
          whileInView="animate"
          viewport={{ once: true, margin: "-80px" }}
          variants={staggerContainerVariants}
          className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
        >
          {integrations.map((item) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.name}
                variants={cardRevealVariants}
                className="flex flex-col items-center rounded-2xl border border-border/80 bg-secondary/40 p-6 text-center transition-colors hover:border-primary/30 hover:bg-secondary/60"
              >
                <div className="flex size-12 items-center justify-center rounded-2xl bg-card">
                  <Icon className="size-6 text-primary" aria-hidden="true" />
                </div>
                <h3 className="mt-4 text-sm font-semibold">{item.name}</h3>
                <p className="mt-1 text-xs text-text-secondary">
                  {item.description}
                </p>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
