import type { LucideIcon } from "lucide-react";

export type IntegrationStatus = "connected" | "disconnected" | "coming_soon";

export type IntegrationStat = {
  label: string;
  value: string;
};

export type IntegrationDefinition = {
  id: string;
  name: string;
  description: string;
  icon: LucideIcon;
  status: IntegrationStatus;
};

export type IntegrationCategory = {
  id: string;
  title: string;
  emoji: string;
  integrations: IntegrationDefinition[];
};
