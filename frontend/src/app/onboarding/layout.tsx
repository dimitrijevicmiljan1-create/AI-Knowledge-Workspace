import { OnboardingGuard } from "@/components/auth/auth-guard";

export default function OnboardingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <OnboardingGuard>
      <div className="flex min-h-screen flex-col bg-background">
        <main className="flex flex-1 items-center justify-center p-4 sm:p-6">
          <div className="w-full max-w-lg">{children}</div>
        </main>
      </div>
    </OnboardingGuard>
  );
}
