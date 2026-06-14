import { GuestGuard } from "@/components/auth/auth-guard";
import { AuthBrand } from "@/components/auth/auth-brand";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <GuestGuard>
      <div className="relative flex min-h-screen flex-col bg-background">
        <div
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(139,92,246,0.12),_transparent_50%)]"
          aria-hidden="true"
        />
        <main className="relative flex flex-1 flex-col items-center justify-center p-4 sm:p-8">
          <div className="mb-8">
            <AuthBrand />
          </div>
          <div className="w-full max-w-md">{children}</div>
        </main>
      </div>
    </GuestGuard>
  );
}
