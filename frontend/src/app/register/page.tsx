import { RegisterForm } from "@/components/auth/register-form";

export default function RegisterPage() {
  return (
    <section className="mx-auto w-full max-w-md space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="text-2xl font-bold tracking-tight">Create account</h2>
        <p className="text-sm text-text-secondary">
          Register to start using AI Knowledge Workspace.
        </p>
      </div>

      <RegisterForm />
    </section>
  );
}
