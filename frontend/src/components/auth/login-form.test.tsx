import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { LoginForm } from "@/components/auth/login-form";
import { renderWithProviders } from "@/test/test-utils";

const push = vi.fn();
const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, refresh }),
}));

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    login: vi.fn().mockResolvedValue(undefined),
    isLoggingIn: false,
  }),
}));

vi.mock("@/lib/api/workspaces", () => ({
  listWorkspaces: vi.fn().mockResolvedValue({ items: [], total: 0 }),
}));

describe("LoginForm", () => {
  beforeEach(() => {
    push.mockReset();
    refresh.mockReset();
  });

  it("renders email and password fields", () => {
    renderWithProviders(<LoginForm />);

    expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("shows forgot password placeholder", () => {
    renderWithProviders(<LoginForm />);
    expect(screen.getByText(/forgot password\?/i)).toBeInTheDocument();
  });

  it("redirects to onboarding when user has no workspaces", async () => {
    const user = userEvent.setup();
    renderWithProviders(<LoginForm />);

    await user.type(screen.getByLabelText(/^email$/i), "user@example.com");
    await user.type(screen.getByLabelText(/^password$/i), "password123");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(push).toHaveBeenCalledWith("/onboarding");
    });
  });
});
