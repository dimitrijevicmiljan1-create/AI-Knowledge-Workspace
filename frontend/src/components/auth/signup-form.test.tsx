import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { SignupForm } from "@/components/auth/signup-form";
import { renderWithProviders } from "@/test/test-utils";

const push = vi.fn();
const refresh = vi.fn();
const register = vi.fn().mockResolvedValue(undefined);
const login = vi.fn().mockResolvedValue(undefined);

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, refresh }),
}));

vi.mock("@/hooks/use-auth", () => ({
  useAuth: () => ({
    register,
    login,
    isRegistering: false,
  }),
}));

describe("SignupForm", () => {
  beforeEach(() => {
    push.mockReset();
    refresh.mockReset();
    register.mockClear();
    login.mockClear();
  });

  it("renders signup fields", () => {
    renderWithProviders(<SignupForm />);

    expect(screen.getByLabelText(/^name$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^confirm password$/i)).toBeInTheDocument();
  });

  it("validates matching passwords", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SignupForm />);

    await user.type(screen.getByLabelText(/^name$/i), "Jane");
    await user.type(screen.getByLabelText(/^email$/i), "jane@example.com");
    await user.type(screen.getByLabelText(/^password$/i), "password123");
    await user.type(
      screen.getByLabelText(/^confirm password$/i),
      "different123",
    );
    await user.click(screen.getByRole("button", { name: /create account/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /passwords do not match/i,
    );
    expect(register).not.toHaveBeenCalled();
  });

  it("registers, signs in, and redirects to onboarding", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SignupForm />);

    await user.type(screen.getByLabelText(/^name$/i), "Jane");
    await user.type(screen.getByLabelText(/^email$/i), "jane@example.com");
    await user.type(screen.getByLabelText(/^password$/i), "password123");
    await user.type(
      screen.getByLabelText(/^confirm password$/i),
      "password123",
    );
    await user.click(screen.getByRole("button", { name: /create account/i }));

    await waitFor(() => {
      expect(register).toHaveBeenCalled();
      expect(login).toHaveBeenCalled();
      expect(push).toHaveBeenCalledWith("/onboarding");
    });
  });
});
