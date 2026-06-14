import { AuthGuard } from "@/components/auth/auth-guard";
import { OnboardingRedirect } from "@/components/auth/onboarding-redirect";
import { AppShell } from "@/components/layout/app-shell";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <OnboardingRedirect>
        <AppShell>{children}</AppShell>
      </OnboardingRedirect>
    </AuthGuard>
  );
}
