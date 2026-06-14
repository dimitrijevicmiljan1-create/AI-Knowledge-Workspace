import Link from "next/link";

import { SignupForm } from "@/components/auth/signup-form";
import { routes } from "@/lib/routes";

export default function SignupPage() {
  return (
    <div className="space-y-2">
      <div className="mb-6 space-y-1 text-center">
        <h1 className="text-page-title text-xl sm:text-2xl">Create your account</h1>
        <p className="text-sm text-text-secondary">Start organizing your knowledge</p>
      </div>
      <SignupForm />
      <p className="text-center text-meta">
        <Link href={routes.home} className="text-primary hover:underline">
          Back to home
        </Link>
      </p>
    </div>
  );
}
