"use client";

import type { LucideIcon } from "lucide-react";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import type { IntegrationStat, IntegrationStatus } from "@/lib/integrations/types";
import { cn } from "@/lib/utils";

type IntegrationCardProps = {
  name: string;
  description: string;
  icon: LucideIcon;
  status: IntegrationStatus;
  stats?: IntegrationStat[];
  connectLabel?: string;
  onConnect?: () => void;
  isConnecting?: boolean;
  manageLabel?: string;
  onManage?: () => void;
  isExpanded?: boolean;
  className?: string;
};

function statusBadge(status: IntegrationStatus) {
  switch (status) {
    case "connected":
      return <StatusBadge label="Connected" variant="success" />;
    case "disconnected":
      return <StatusBadge label="Not connected" variant="warning" />;
    case "coming_soon":
      return <StatusBadge label="Coming soon" variant="info" />;
  }
}

export function IntegrationCard({
  name,
  description,
  icon: Icon,
  status,
  stats = [],
  connectLabel = "Connect",
  onConnect,
  isConnecting = false,
  manageLabel = "Manage",
  onManage,
  isExpanded = false,
  className,
}: IntegrationCardProps) {
  const isComingSoon = status === "coming_soon";
  const isConnected = status === "connected";

  return (
    <Card
      className={cn(
        "flex h-full flex-col transition-colors",
        isExpanded && "border-primary/40 ring-1 ring-primary/20",
        className,
      )}
    >
      <CardHeader className="space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10">
              <Icon className="size-5 text-primary" aria-hidden="true" />
            </div>
            <div className="min-w-0">
              <CardTitle className="text-base">{name}</CardTitle>
              {statusBadge(status)}
            </div>
          </div>
        </div>
        <CardDescription className="line-clamp-3">{description}</CardDescription>
      </CardHeader>

      <CardContent className="mt-auto space-y-4">
        {stats.length > 0 ? (
          <dl className="grid grid-cols-2 gap-3">
            {stats.map((stat) => (
              <div key={stat.label} className="rounded-lg border border-border bg-surface px-3 py-2">
                <dt className="text-meta">{stat.label}</dt>
                <dd className="text-sm font-medium">{stat.value}</dd>
              </div>
            ))}
          </dl>
        ) : null}

        <div className="flex flex-wrap gap-2">
          {isComingSoon ? (
            <Button type="button" size="sm" disabled>
              {connectLabel}
            </Button>
          ) : isConnected ? (
            onManage ? (
              <Button
                type="button"
                size="sm"
                variant={isExpanded ? "default" : "secondary"}
                onClick={onManage}
              >
                {manageLabel}
              </Button>
            ) : null
          ) : onConnect ? (
            <Button
              type="button"
              size="sm"
              onClick={onConnect}
              disabled={isConnecting}
            >
              {isConnecting ? (
                <Loader2 className="size-4 animate-spin" />
              ) : null}
              {connectLabel}
            </Button>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
