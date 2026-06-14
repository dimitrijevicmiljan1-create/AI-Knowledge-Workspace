"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { Skeleton } from "@/components/ui/skeleton";
import { useWorkspaces } from "@/hooks/use-workspaces";
import { routes } from "@/lib/routes";

export function OnboardingRedirect({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { data: workspaces, isLoading } = useWorkspaces(true);

  useEffect(() => {
    if (!isLoading && workspaces && workspaces.total === 0) {
      router.replace(routes.onboarding);
    }
  }, [isLoading, router, workspaces]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Skeleton className="h-8 w-48" />
      </div>
    );
  }

  if (workspaces && workspaces.total === 0) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Skeleton className="h-8 w-48" />
      </div>
    );
  }

  return children;
}
