"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

import { buttonVariants } from "@/components/ui/button";
import { heroVariants, transitionDefault } from "@/lib/motion";
import { routes } from "@/lib/routes";
import { cn } from "@/lib/utils";

export function Hero() {
  return (
    <section className="relative overflow-hidden px-4 pb-8 pt-16 sm:px-6 sm:pt-24 lg:pt-28">
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(139,92,246,0.18),_transparent_55%)]"
        aria-hidden="true"
      />
      <div className="relative mx-auto max-w-7xl">
        <motion.div
          initial="initial"
          animate="animate"
          variants={heroVariants}
          transition={transitionDefault}
          className="mx-auto max-w-4xl text-center"
        >
          <p className="mb-4 inline-flex rounded-full border border-border bg-surface px-3 py-1 text-meta">
            Production-grade AI knowledge platform
          </p>
          <h1 className="text-hero">
            Your AI Knowledge
            <span className="block bg-gradient-to-r from-primary via-accent-secondary to-primary bg-clip-text text-transparent">
              Workspace
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-body text-text-secondary">
            Connect documents, GitHub repositories and Obsidian vaults. Ask
            questions. Get answers with citations.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              href={routes.signup}
              className={cn(
                buttonVariants({ size: "lg" }),
                "group w-full shadow-[0_0_32px_rgba(139,92,246,0.25)] sm:w-auto",
              )}
            >
              Start Free
              <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link
              href={routes.login}
              className={cn(
                buttonVariants({ variant: "secondary", size: "lg" }),
                "w-full sm:w-auto",
              )}
            >
              Sign In
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
