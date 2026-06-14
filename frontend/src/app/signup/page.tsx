import Link from "next/link";

import { SignupForm } from "@/components/auth/signup-form";
import { routes } from "@/lib/routes";

export default function SignupPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-2 text-center">
        <Link
          href={routes.home}
          className="inline-flex items-center gap-2 text-sm font-semibold tracking-tight transition-opacity hover:opacity-80"
        >
          <span className="flex size-7 items-center justify-center rounded-md bg-primary text-xs font-bold text-primary-foreground">
            AI
          </span>
          AI Knowledge Workspace
        </Link>
      </div>
      <SignupForm />
    </div>
  );
}
