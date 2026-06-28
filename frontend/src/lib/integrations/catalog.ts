import {
  Building2,
  Cloud,
  Database,
  FileSpreadsheet,
  FileText,
  Kanban,
  Mail,
  MessageSquare,
  NotebookPen,
} from "lucide-react";

import type { IntegrationCategory, IntegrationDefinition } from "@/lib/integrations/types";

function comingSoon(
  id: string,
  name: string,
  description: string,
  icon: IntegrationDefinition["icon"],
): IntegrationDefinition {
  return {
    id,
    name,
    description,
    icon,
    status: "coming_soon",
  };
}

export const integrationCategories: IntegrationCategory[] = [
  {
    id: "google-workspace",
    title: "Google Workspace",
    emoji: "☁",
    integrations: [
      comingSoon(
        "google-drive",
        "Google Drive",
        "Sync files and folders from Google Drive into your knowledge workspace.",
        Cloud,
      ),
      comingSoon(
        "google-docs",
        "Google Docs",
        "Index Google Docs for search and AI-powered answers.",
        FileText,
      ),
      comingSoon(
        "google-sheets",
        "Google Sheets",
        "Bring spreadsheet data into your workspace for analysis and chat.",
        FileSpreadsheet,
      ),
      comingSoon(
        "gmail",
        "Gmail",
        "Search and query email threads with citation-backed responses.",
        Mail,
      ),
    ],
  },
  {
    id: "communication",
    title: "Communication",
    emoji: "💬",
    integrations: [
      comingSoon(
        "slack",
        "Slack",
        "Connect Slack channels and messages to your knowledge base.",
        MessageSquare,
      ),
    ],
  },
  {
    id: "business",
    title: "Business",
    emoji: "💼",
    integrations: [
      comingSoon(
        "hubspot",
        "HubSpot",
        "Sync CRM records, deals, and contacts for AI-assisted workflows.",
        Building2,
      ),
      comingSoon(
        "jira",
        "Jira",
        "Index issues, epics, and project updates from Jira.",
        Kanban,
      ),
    ],
  },
  {
    id: "databases",
    title: "Databases",
    emoji: "🗄",
    integrations: [
      comingSoon(
        "postgresql",
        "PostgreSQL",
        "Query structured data from PostgreSQL databases in natural language.",
        Database,
      ),
      comingSoon(
        "supabase",
        "Supabase",
        "Connect Supabase projects for document and row-level retrieval.",
        Database,
      ),
    ],
  },
];

export const knowledgeComingSoonIntegrations: IntegrationDefinition[] = [
  comingSoon(
    "notion",
    "Notion",
    "Import Notion pages and databases into your workspace.",
    NotebookPen,
  ),
];
