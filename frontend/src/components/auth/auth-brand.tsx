import Link from "next/link";

import { routes } from "@/lib/routes";

export function AuthBrand() {
  return (
    <Link
      href={routes.home}
      className="group inline-flex flex-col items-center gap-3 text-center transition-opacity hover:opacity-90"
    >
      <span className="flex size-12 items-center justify-center rounded-2xl bg-primary text-lg font-bold text-primary-foreground shadow-[0_0_40px_rgba(139,92,246,0.35)] transition-transform group-hover:scale-[1.02]">
        AI
      </span>
      <div>
        <p className="text-lg font-semibold tracking-tight">AI Knowledge Workspace</p>
        <p className="text-meta">Your knowledge, searchable and intelligent</p>
      </div>
    </Link>
  );
}
