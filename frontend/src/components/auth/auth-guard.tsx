"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/use-auth";
import { routes } from "@/lib/routes";
import { hasStoredSession } from "@/lib/auth-storage";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!hasStoredSession()) {
      router.replace(routes.login);
      return;
    }
    if (!isLoading && !isAuthenticated) {
      router.replace(routes.login);
    }
  }, [isAuthenticated, isLoading, router]);

  if (!hasStoredSession() || isLoading || !isAuthenticated) {
    return <AuthGuardSkeleton />;
  }

  return children;
}

export function GuestGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      router.replace(routes.chat);
    }
  }, [isAuthenticated, router]);

  if (hasStoredSession() && (isLoading || isAuthenticated)) {
    return <AuthGuardSkeleton />;
  }

  return children;
}

function AuthGuardSkeleton() {
  return (
    <div
      className="flex min-h-[50vh] flex-col items-center justify-center gap-4 p-6"
      role="status"
      aria-label="Loading"
    >
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-4 w-64" />
    </div>
  );
}
