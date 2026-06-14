import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

import { PublicNavbar } from "@/components/layout/public-navbar";

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    isAuthenticated: false,
    isLoading: false,
  }),
}));

vi.mock("@/hooks/use-workspaces", () => ({
  useWorkspaces: () => ({
    data: undefined,
    isLoading: false,
  }),
}));

vi.mock("@/lib/auth-storage", () => ({
  hasStoredSession: () => false,
}));

describe("PublicNavbar", () => {
  it("renders logo, section links, and auth CTAs", () => {
    render(<PublicNavbar />);

    expect(
      screen.getByRole("link", { name: /ai knowledge workspace home/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /^features$/i })).toHaveAttribute(
      "href",
      "#features",
    );
    expect(screen.getAllByRole("link", { name: /^sign in$/i })[0]).toHaveAttribute(
      "href",
      "/login",
    );
    expect(
      screen.getAllByRole("link", { name: /get started/i })[0],
    ).toHaveAttribute("href", "/signup");
  });
});
