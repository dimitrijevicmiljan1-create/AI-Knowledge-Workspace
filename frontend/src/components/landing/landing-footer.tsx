import Link from "next/link";

import { routes } from "@/lib/routes";

export function LandingFooter() {
  return (
    <footer className="border-t border-border bg-surface">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-3 lg:col-span-2">
            <div className="flex items-center gap-2">
              <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-sm font-bold text-primary-foreground">
                AI
              </span>
              <span className="font-semibold">AI Knowledge Workspace</span>
            </div>
            <p className="max-w-sm text-sm text-text-secondary">
              Connect documents, GitHub repositories and Obsidian vaults. Ask
              questions. Get answers with citations.
            </p>
          </div>
          <div>
            <h3 className="text-sm font-semibold">Product</h3>
            <ul className="mt-3 space-y-2 text-sm text-text-secondary">
              <li>
                <Link href="#features" className="hover:text-foreground">
                  Features
                </Link>
              </li>
              <li>
                <Link href="#pricing" className="hover:text-foreground">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="#documentation" className="hover:text-foreground">
                  Documentation
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold">Account</h3>
            <ul className="mt-3 space-y-2 text-sm text-text-secondary">
              <li>
                <Link href={routes.login} className="hover:text-foreground">
                  Sign In
                </Link>
              </li>
              <li>
                <Link href={routes.signup} className="hover:text-foreground">
                  Get Started
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-10 border-t border-border pt-6 text-meta">
          © {new Date().getFullYear()} AI Knowledge Workspace
        </div>
      </div>
    </footer>
  );
}
