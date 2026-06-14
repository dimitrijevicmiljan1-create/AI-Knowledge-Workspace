import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <section className="mx-auto w-full max-w-md space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="text-2xl font-bold tracking-tight">Sign in</h2>
        <p className="text-sm text-text-secondary">
          Access your workspaces and knowledge sources.
        </p>
      </div>

      <LoginForm />
    </section>
  );
}
