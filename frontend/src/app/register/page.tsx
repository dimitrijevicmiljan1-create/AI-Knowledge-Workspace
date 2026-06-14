import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function RegisterPage() {
  return (
    <section className="mx-auto w-full max-w-md space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="text-2xl font-bold tracking-tight">Create account</h2>
        <p className="text-sm text-text-secondary">
          Get started with AI Knowledge Workspace.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Register</CardTitle>
          <CardDescription>
            User registration will be wired in a future phase. This form follows
            the global design system.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="name">
              Full name
            </label>
            <div className="h-9 rounded-lg border border-input bg-secondary px-3 text-sm text-muted-foreground">
              Jane Developer
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="email">
              Email
            </label>
            <div className="h-9 rounded-lg border border-input bg-secondary px-3 text-sm text-muted-foreground">
              you@company.com
            </div>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}
