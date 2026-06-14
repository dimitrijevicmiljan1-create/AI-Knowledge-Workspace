import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function LoginPage() {
  return (
    <section className="mx-auto w-full max-w-md space-y-6">
      <div className="space-y-2 text-center">
        <h2 className="text-2xl font-bold tracking-tight">Sign in</h2>
        <p className="text-sm text-text-secondary">
          Welcome back. Enter your credentials to continue.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Login</CardTitle>
          <CardDescription>
            Authentication will be wired in a future phase. This form follows the
            global design system.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="email">
              Email
            </label>
            <div className="h-9 rounded-lg border border-input bg-secondary px-3 text-sm text-muted-foreground">
              you@company.com
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium" htmlFor="password">
              Password
            </label>
            <div className="h-9 rounded-lg border border-input bg-secondary px-3 text-sm text-muted-foreground">
              ••••••••
            </div>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}
