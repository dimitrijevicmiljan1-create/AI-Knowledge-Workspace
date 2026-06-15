"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, LogOut, Menu, Bell } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { useSidebar } from "@/components/layout/sidebar-context";
import { Button, buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/use-auth";
import { dropdownVariants, transitionFast } from "@/lib/motion";
import { routes } from "@/lib/routes";
import { hasStoredSession } from "@/lib/auth-storage";
import { cn } from "@/lib/utils";

export function Header() {
  const router = useRouter();
  const { isMobile, setMobileOpen } = useSidebar();
  const { user, isLoading, isAuthenticated, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const showAuthLoading = hasStoredSession() && isLoading;

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleLogout() {
    logout();
    router.push(routes.home);
  }

  return (
    <header className="glass-nav sticky top-0 z-30 flex h-14 shrink-0 items-center gap-3 px-3 sm:h-16 sm:gap-4 sm:px-5">
      {isMobile ? (
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={() => setMobileOpen(true)}
          aria-label="Open sidebar"
        >
          <Menu className="size-4" />
        </Button>
      ) : null}

      <div className="ml-auto flex items-center gap-1 sm:gap-2">
        <Button
          variant="ghost"
          size="icon-sm"
          aria-label="Notifications"
          title="Notifications coming soon"
          className="text-text-secondary"
        >
          <Bell className="size-4" />
        </Button>

        {showAuthLoading ? (
          <Skeleton className="size-8 rounded-full" />
        ) : isAuthenticated && user ? (
          <div className="relative" ref={menuRef}>
            <button
              type="button"
              onClick={() => setMenuOpen((open) => !open)}
              className="flex size-8 items-center justify-center rounded-full border border-border bg-elevated text-xs font-semibold uppercase transition-colors hover:bg-surface"
              aria-label="User menu"
              aria-expanded={menuOpen}
              aria-haspopup="menu"
            >
              {(user.full_name ?? user.email).charAt(0)}
            </button>
            <AnimatePresence>
              {menuOpen ? (
                <motion.div
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  variants={dropdownVariants}
                  transition={transitionFast}
                  className="absolute right-0 top-full z-50 mt-2 w-56 overflow-hidden rounded-xl border border-border bg-elevated py-1 shadow-xl"
                  role="menu"
                >
                  <div className="border-b border-border px-3 py-2.5">
                    <p className="truncate text-sm font-medium">
                      {user.full_name ?? "User"}
                    </p>
                    <p className="truncate text-meta">{user.email}</p>
                  </div>
                  <Link
                    href={routes.settings}
                    className="block px-3 py-2 text-sm text-text-secondary hover:bg-accent hover:text-foreground"
                    role="menuitem"
                    onClick={() => setMenuOpen(false)}
                  >
                    Settings
                  </Link>
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 px-3 py-2 text-sm text-text-secondary hover:bg-accent hover:text-foreground"
                    role="menuitem"
                    onClick={handleLogout}
                  >
                    <LogOut className="size-4" />
                    Sign out
                  </button>
                </motion.div>
              ) : null}
            </AnimatePresence>
          </div>
        ) : (
          <Link href={routes.login} className={cn(buttonVariants({ size: "sm" }))}>
            Sign in
          </Link>
        )}
      </div>
    </header>
  );
}

export function AuthSuccessBanner({ message }: { message: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-4 flex items-center gap-2 rounded-xl border border-success/30 bg-success/10 px-3 py-2 text-sm text-success"
      role="status"
    >
      <CheckCircle2 className="size-4 shrink-0" />
      {message}
    </motion.div>
  );
}
