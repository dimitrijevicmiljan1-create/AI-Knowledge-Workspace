"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { LogOut, Menu } from "lucide-react";

import { useSidebar } from "@/components/layout/sidebar-context";
import { Button, buttonVariants } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/use-auth";
import { hasStoredSession } from "@/lib/auth-storage";
import { cn } from "@/lib/utils";

export function Header() {
  const router = useRouter();
  const { isMobile, setMobileOpen } = useSidebar();
  const { user, isLoading, isAuthenticated, logout } = useAuth();
  const showAuthLoading = hasStoredSession() && isLoading;

  function handleLogout() {
    logout();
    router.push("/");
  }

  return (
    <header className="sticky top-0 z-30 flex h-16 shrink-0 items-center justify-between border-b border-border bg-background/80 px-4 backdrop-blur-md sm:px-6">
      <div className="flex items-center gap-3">
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
        <div>
          <h1 className="text-base font-semibold tracking-tight">
            AI Knowledge Workspace
          </h1>
          {showAuthLoading ? (
            <Skeleton className="mt-1 h-3 w-32" />
          ) : isAuthenticated && user ? (
            <p className="text-xs text-text-secondary sm:text-sm">
              {user.full_name ?? user.email}
            </p>
          ) : (
            <p className="text-xs text-text-secondary sm:text-sm">
              Sign in to access your account
            </p>
          )}
        </div>
      </div>
      <div className="flex items-center gap-2">
        {showAuthLoading ? (
          <Skeleton className="h-7 w-20" />
        ) : isAuthenticated ? (
          <Button variant="ghost" size="sm" onClick={handleLogout}>
            <LogOut className="size-4" />
            Sign out
          </Button>
        ) : (
          <>
            <Link
              href="/login"
              className={cn(buttonVariants({ variant: "ghost", size: "sm" }))}
            >
              Sign in
            </Link>
            <Link
              href="/signup"
              className={cn(buttonVariants({ size: "sm" }))}
            >
              Register
            </Link>
          </>
        )}
      </div>
    </header>
  );
}
