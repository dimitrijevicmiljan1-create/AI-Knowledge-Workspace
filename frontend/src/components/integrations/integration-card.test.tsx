import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Cloud, FolderGit2 } from "lucide-react";

import { IntegrationCard } from "@/components/integrations/integration-card";
import { IntegrationSection } from "@/components/integrations/integration-section";
import {
  integrationCategories,
  knowledgeComingSoonIntegrations,
} from "@/lib/integrations/catalog";

describe("IntegrationCard", () => {
  it("renders a connected integration with stats and manage action", () => {
    const onManage = vi.fn();

    render(
      <IntegrationCard
        name="GitHub"
        description="Connect repositories."
        icon={FolderGit2}
        status="connected"
        stats={[
          { label: "Repositories", value: "3" },
          { label: "Last sync", value: "Today" },
        ]}
        onManage={onManage}
      />,
    );

    expect(screen.getByText("GitHub")).toBeInTheDocument();
    expect(screen.getByText("Connected")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Manage" })).toBeInTheDocument();
  });

  it("renders a coming soon integration with a disabled connect button", () => {
    render(
      <IntegrationCard
        name="Slack"
        description="Connect Slack channels."
        icon={Cloud}
        status="coming_soon"
      />,
    );

    expect(screen.getByText("Coming soon")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Connect" })).toBeDisabled();
  });

  it("calls onConnect for disconnected integrations", async () => {
    const user = userEvent.setup();
    const onConnect = vi.fn();

    render(
      <IntegrationCard
        name="GitHub"
        description="Connect repositories."
        icon={FolderGit2}
        status="disconnected"
        onConnect={onConnect}
        connectLabel="Connect GitHub"
      />,
    );

    await user.click(screen.getByRole("button", { name: "Connect GitHub" }));
    expect(onConnect).toHaveBeenCalledOnce();
  });
});

describe("IntegrationSection", () => {
  it("renders a categorized section heading", () => {
    render(
      <IntegrationSection title="Knowledge" emoji="📚">
        <p>Cards go here</p>
      </IntegrationSection>,
    );

    expect(screen.getByRole("heading", { name: /Knowledge/i })).toBeInTheDocument();
    expect(screen.getByText("Cards go here")).toBeInTheDocument();
  });
});

describe("integrations catalog", () => {
  it("includes knowledge placeholders and future integration categories", () => {
    expect(knowledgeComingSoonIntegrations.map((item) => item.name)).toEqual([
      "Notion",
    ]);
    expect(integrationCategories.map((category) => category.title)).toEqual([
      "Google Workspace",
      "Communication",
      "Business",
      "Databases",
    ]);
  });
});
