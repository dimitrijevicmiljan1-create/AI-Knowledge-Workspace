"use client";

import { motion } from "framer-motion";
import {
  BookMarked,
  Brain,
  FolderGit2,
  MessageSquare,
  Search,
  Sparkles,
} from "lucide-react";

import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  cardRevealVariants,
  staggerContainerVariants,
} from "@/lib/motion";

const features = [
  {
    title: "GitHub Integration",
    description: "Sync repositories and search code alongside your docs.",
    icon: FolderGit2,
  },
  {
    title: "Obsidian Integration",
    description: "Connect vaults and make your notes instantly searchable.",
    icon: BookMarked,
  },
  {
    title: "AI Search",
    description: "Find answers across all sources with natural language queries.",
    icon: Search,
  },
  {
    title: "AI Chat",
    description: "Chat with your knowledge base and get cited, grounded answers.",
    icon: MessageSquare,
  },
  {
    title: "Conversation Memory",
    description: "Persistent context across sessions for deeper follow-ups.",
    icon: Brain,
  },
  {
    title: "Semantic Search",
    description: "Vector-powered retrieval that understands meaning, not just keywords.",
    icon: Sparkles,
  },
];

export function Features() {
  return (
    <section
      id="features"
      className="border-t border-border/60 px-4 py-20 sm:px-6"
      aria-labelledby="features-heading"
    >
      <div className="mx-auto max-w-7xl">
        <div className="mx-auto max-w-2xl text-center">
          <h2
            id="features-heading"
            className="text-2xl font-bold tracking-tight sm:text-3xl"
          >
            Everything you need to work with knowledge
          </h2>
          <p className="mt-3 text-text-secondary">
            A focused toolkit for developers and teams who live in docs, repos,
            and notes.
          </p>
        </div>

        <motion.div
          initial="initial"
          whileInView="animate"
          viewport={{ once: true, margin: "-80px" }}
          variants={staggerContainerVariants}
          className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
        >
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <motion.div key={feature.title} variants={cardRevealVariants}>
                <Card className="h-full border-border/80 bg-card/80 transition-colors hover:border-primary/30">
                  <CardHeader>
                    <div className="mb-2 flex size-10 items-center justify-center rounded-xl bg-primary/10">
                      <Icon className="size-5 text-primary" aria-hidden="true" />
                    </div>
                    <CardTitle>{feature.title}</CardTitle>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
