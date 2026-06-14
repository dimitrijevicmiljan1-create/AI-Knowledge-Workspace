import { AuthGuard } from "@/components/auth/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { OnboardingRedirect } from "@/components/auth/onboarding-redirect";

export default function DashboardLayout({
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
