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
    <section className="relative overflow-hidden px-4 py-20 sm:px-6 sm:py-28 lg:py-32">
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(139,92,246,0.15),_transparent_50%)]"
        aria-hidden="true"
      />
      <div className="relative mx-auto max-w-7xl">
        <motion.div
          initial="initial"
          animate="animate"
          variants={heroVariants}
          transition={transitionDefault}
          className="mx-auto max-w-3xl text-center"
        >
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
            Your Knowledge.
            <br />
            <span className="text-primary">Searchable. Chatable. Intelligent.</span>
          </h1>
          <p className="mt-6 text-base text-text-secondary sm:text-lg">
            Connect GitHub repositories, Obsidian vaults and documents. Search
            everything instantly and chat with your knowledge using AI.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              href={routes.signup}
              className={cn(
                buttonVariants({ size: "lg" }),
                "group w-full sm:w-auto",
              )}
            >
              Get Started
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
