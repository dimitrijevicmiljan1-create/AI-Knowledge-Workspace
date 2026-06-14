import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { OnboardingForm } from "@/components/auth/onboarding-form";
import { renderWithProviders } from "@/test/test-utils";

const push = vi.fn();
const refresh = vi.fn();
const mutateAsync = vi.fn().mockResolvedValue({ id: "ws-1", name: "Test" });

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, refresh }),
}));

vi.mock("@/hooks/use-workspaces", () => ({
  useCreateWorkspace: () => ({
    mutateAsync,
    isPending: false,
  }),
}));

describe("OnboardingForm", () => {
  beforeEach(() => {
    push.mockReset();
    refresh.mockReset();
    mutateAsync.mockClear();
  });

  it("renders workspace creation fields", () => {
    renderWithProviders(<OnboardingForm />);

    expect(screen.getByLabelText(/workspace name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /create workspace/i }),
    ).toBeInTheDocument();
  });

  it("creates workspace and redirects to dashboard", async () => {
    const user = userEvent.setup();
    renderWithProviders(<OnboardingForm />);

    await user.type(screen.getByLabelText(/workspace name/i), "Engineering");
    await user.click(screen.getByRole("button", { name: /create workspace/i }));

    await waitFor(() => {
      expect(mutateAsync).toHaveBeenCalledWith(
        expect.objectContaining({ name: "Engineering" }),
      );
      expect(push).toHaveBeenCalledWith("/dashboard");
    });
  });
});
