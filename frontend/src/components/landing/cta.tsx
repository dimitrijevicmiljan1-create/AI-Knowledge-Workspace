"use client";

import Link from "next/link";
import { motion } from "framer-motion";

import { buttonVariants } from "@/components/ui/button";
import { heroVariants, transitionDefault } from "@/lib/motion";
import { routes } from "@/lib/routes";
import { cn } from "@/lib/utils";

export function Cta() {
  return (
    <section
      className="border-t border-border/60 px-4 py-20 sm:px-6"
      aria-labelledby="cta-heading"
    >
      <motion.div
        initial="initial"
        whileInView="animate"
        viewport={{ once: true }}
        variants={heroVariants}
        transition={transitionDefault}
        className="mx-auto max-w-3xl rounded-2xl border border-primary/20 bg-card/60 px-6 py-14 text-center sm:px-10"
      >
        <h2
          id="cta-heading"
          className="text-2xl font-bold tracking-tight sm:text-3xl"
        >
          Ready to organize your knowledge?
        </h2>
        <p className="mt-3 text-text-secondary">
          Create your account and set up your first workspace in minutes.
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link
            href={routes.signup}
            className={cn(buttonVariants({ size: "lg" }), "w-full sm:w-auto")}
          >
            Create Account
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
    </section>
  );
}
