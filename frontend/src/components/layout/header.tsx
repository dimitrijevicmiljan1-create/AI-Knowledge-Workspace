"use client";

import { Menu } from "lucide-react";

import { useSidebar } from "@/components/layout/sidebar-context";
import { Button } from "@/components/ui/button";

export function Header() {
  const { isMobile, setMobileOpen } = useSidebar();

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
          <p className="text-xs text-text-secondary sm:text-sm">
            Modern AI SaaS for knowledge work
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Button variant="secondary" size="sm">
          Get started
        </Button>
      </div>
    </header>
  );
}
