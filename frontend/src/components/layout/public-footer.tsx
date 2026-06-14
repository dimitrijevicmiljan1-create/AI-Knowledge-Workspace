import Link from "next/link";

import { routes } from "@/lib/routes";

export function PublicFooter() {
  return (
    <footer className="border-t border-border/60 bg-background">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-10 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <div className="space-y-1">
          <p className="text-sm font-semibold">AI Knowledge Workspace</p>
          <p className="text-sm text-text-secondary">
            Your knowledge, searchable, chatable, intelligent.
          </p>
        </div>
        <nav
          className="flex flex-wrap gap-4 text-sm text-text-secondary"
          aria-label="Footer navigation"
        >
          <Link href={routes.login} className="transition-colors hover:text-foreground">
            Sign In
          </Link>
          <Link href={routes.signup} className="transition-colors hover:text-foreground">
            Get Started
          </Link>
        </nav>
      </div>
      <div className="border-t border-border/40 px-4 py-4 sm:px-6">
        <p className="mx-auto max-w-7xl text-xs text-muted-foreground">
          © {new Date().getFullYear()} AI Knowledge Workspace. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
