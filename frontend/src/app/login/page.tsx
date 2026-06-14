import Link from "next/link";

import { LoginForm } from "@/components/auth/login-form";
import { routes } from "@/lib/routes";

export default function LoginPage() {
  return (
    <div className="space-y-2">
      <div className="mb-6 space-y-1 text-center">
        <h1 className="text-page-title text-xl sm:text-2xl">Welcome back</h1>
        <p className="text-sm text-text-secondary">Sign in to your workspace</p>
      </div>
      <LoginForm />
      <p className="text-center text-meta">
        <Link href={routes.home} className="text-primary hover:underline">
          Back to home
        </Link>
      </p>
    </div>
  );
}
