"use client";

import { motion } from "framer-motion";
import {
  Brain,
  FileText,
  MessageSquare,
  Quote,
  Search,
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
    title: "Knowledge Sources",
    description: "Documents, GitHub, and Obsidian in one workspace.",
    icon: FileText,
    items: ["Documents", "GitHub", "Obsidian"],
  },
  {
    title: "AI Search",
    description: "Semantic search across every connected source.",
    icon: Search,
  },
  {
    title: "RAG Chat",
    description: "Ask questions and receive grounded, cited answers.",
    icon: MessageSquare,
  },
  {
    title: "Conversation Memory",
    description: "Persistent context for deeper follow-up questions.",
    icon: Brain,
  },
  {
    title: "Citations",
    description: "Every answer links back to source material.",
    icon: Quote,
  },
];

export function Features() {
  return (
    <section
      id="features"
      className="border-t border-border px-4 py-20 sm:px-6"
      aria-labelledby="features-heading"
    >
      <div className="mx-auto max-w-7xl">
        <div className="mx-auto max-w-2xl text-center">
          <h2 id="features-heading" className="text-section-title sm:text-3xl">
            Built for knowledge work at scale
          </h2>
          <p className="mt-3 text-body text-text-secondary">
            Search, chat, and cite — without switching tools.
          </p>
        </div>

        <motion.div
          initial="initial"
          whileInView="animate"
          viewport={{ once: true, margin: "-80px" }}
          variants={staggerContainerVariants}
          className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-3"
        >
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <motion.div key={feature.title} variants={cardRevealVariants}>
                <Card className="h-full border-border/80 bg-elevated/80 transition-all duration-200 hover:border-primary/30 hover:shadow-[0_8px_32px_rgba(0,0,0,0.35)]">
                  <CardHeader>
                    <div className="mb-3 flex size-10 items-center justify-center rounded-xl bg-primary/10">
                      <Icon className="size-5 text-primary" aria-hidden="true" />
                    </div>
                    <CardTitle>{feature.title}</CardTitle>
                    <CardDescription>{feature.description}</CardDescription>
                    {feature.items ? (
                      <ul className="mt-3 flex flex-wrap gap-2">
                        {feature.items.map((item) => (
                          <li
                            key={item}
                            className="rounded-md border border-border bg-surface px-2 py-1 text-meta"
                          >
                            {item}
                          </li>
                        ))}
                      </ul>
                    ) : null}
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
