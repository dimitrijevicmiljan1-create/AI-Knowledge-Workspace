"use client";

import Link from "next/link";
import { Menu, X } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";

import { Button, buttonVariants } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { useWorkspaces } from "@/hooks/use-workspaces";
import { backdropVariants, transitionFast } from "@/lib/motion";
import { routes } from "@/lib/routes";
import { cn } from "@/lib/utils";
import { hasStoredSession } from "@/lib/auth-storage";

const navLinks = [
  { label: "Features", href: "#features" },
  { label: "Pricing", href: "#pricing" },
  { label: "Documentation", href: "#documentation" },
];

export function PublicNavbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isAuthenticated, isLoading } = useAuth();
  const { data: workspaces, isLoading: isWorkspacesLoading } = useWorkspaces(
    isAuthenticated,
  );

  const showAuthLoading =
    hasStoredSession() && (isLoading || (isAuthenticated && isWorkspacesLoading));

  const workspaceHref =
    isAuthenticated && workspaces && workspaces.total > 0
      ? routes.dashboard
      : isAuthenticated
        ? routes.onboarding
        : routes.signup;

  return (
    <header className="glass-nav sticky top-0 z-50">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link
          href={routes.home}
          className="flex items-center gap-2.5 transition-opacity hover:opacity-80"
          aria-label="AI Knowledge Workspace home"
        >
          <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-sm font-bold text-primary-foreground shadow-[0_0_24px_rgba(139,92,246,0.35)]">
            AI
          </span>
          <span className="hidden text-sm font-semibold tracking-tight sm:inline">
            AI Knowledge Workspace
          </span>
        </Link>

        <nav
          className="hidden items-center gap-1 md:flex"
          aria-label="Primary navigation"
        >
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-lg px-3 py-2 text-sm text-text-secondary transition-colors hover:bg-accent hover:text-foreground"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          {showAuthLoading ? (
            <div className="h-8 w-36 animate-pulse rounded-lg bg-muted" />
          ) : isAuthenticated ? (
            <Link href={workspaceHref} className={cn(buttonVariants({ size: "sm" }))}>
              Open Workspace
            </Link>
          ) : (
            <>
              <Link
                href={routes.login}
                className={cn(buttonVariants({ variant: "ghost", size: "sm" }))}
              >
                Sign In
              </Link>
              <Link href={routes.signup} className={cn(buttonVariants({ size: "sm" }))}>
                Get Started
              </Link>
            </>
          )}
        </div>

        <Button
          variant="ghost"
          size="icon-sm"
          className="md:hidden"
          onClick={() => setMobileOpen(true)}
          aria-label="Open navigation menu"
          aria-expanded={mobileOpen}
        >
          <Menu className="size-4" />
        </Button>
      </div>

      <AnimatePresence>
        {mobileOpen ? (
          <>
            <motion.div
              initial="initial"
              animate="animate"
              exit="exit"
              variants={backdropVariants}
              transition={transitionFast}
              className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm md:hidden"
              onClick={() => setMobileOpen(false)}
              aria-hidden="true"
            />
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={transitionFast}
              className="fixed inset-y-0 right-0 z-50 flex w-72 flex-col border-l border-border bg-surface p-6 md:hidden"
              role="dialog"
              aria-modal="true"
              aria-label="Mobile navigation"
            >
              <div className="mb-6 flex items-center justify-between">
                <span className="text-sm font-semibold">Menu</span>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={() => setMobileOpen(false)}
                  aria-label="Close navigation menu"
                >
                  <X className="size-4" />
                </Button>
              </div>
              <nav className="flex flex-col gap-1" aria-label="Mobile navigation">
                {navLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="rounded-lg px-3 py-2.5 text-sm text-text-secondary hover:bg-accent hover:text-foreground"
                    onClick={() => setMobileOpen(false)}
                  >
                    {link.label}
                  </Link>
                ))}
              </nav>
              <div className="mt-6 flex flex-col gap-2 border-t border-border pt-6">
                {showAuthLoading ? (
                  <div className="h-9 w-full animate-pulse rounded-lg bg-muted" />
                ) : isAuthenticated ? (
                  <Link
                    href={workspaceHref}
                    className={cn(buttonVariants({ size: "default" }), "w-full")}
                    onClick={() => setMobileOpen(false)}
                  >
                    Open Workspace
                  </Link>
                ) : (
                  <>
                    <Link
                      href={routes.login}
                      className={cn(
                        buttonVariants({ variant: "outline", size: "default" }),
                        "w-full",
                      )}
                      onClick={() => setMobileOpen(false)}
                    >
                      Sign In
                    </Link>
                    <Link
                      href={routes.signup}
                      className={cn(buttonVariants({ size: "default" }), "w-full")}
                      onClick={() => setMobileOpen(false)}
                    >
                      Get Started
                    </Link>
                  </>
                )}
              </div>
            </motion.div>
          </>
        ) : null}
      </AnimatePresence>
    </header>
  );
}
