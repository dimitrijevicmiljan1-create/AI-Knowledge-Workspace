import { LayoutDashboard } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";

export default function DashboardPage() {
  return (
    <section className="space-y-8">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-text-secondary">
          Overview of your workspaces, sources, and recent activity.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {["Workspaces", "Documents", "Conversations"].map((label) => (
          <Card key={label}>
            <CardHeader className="pb-2">
              <CardDescription>{label}</CardDescription>
              <CardTitle className="text-3xl font-bold">—</CardTitle>
            </CardHeader>
            <CardContent>
              <Skeleton className="h-2 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>

      <EmptyState
        icon={<LayoutDashboard className="size-6 text-muted-foreground" />}
        title="No activity yet"
        description="Your recent workspaces and conversations will appear here once you get started."
      />
    </section>
  );
}
