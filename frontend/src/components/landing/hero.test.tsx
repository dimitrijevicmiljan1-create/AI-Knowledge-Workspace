import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { Hero } from "@/components/landing/hero";

describe("Hero", () => {
  it("renders headline and call-to-action buttons", () => {
    render(<Hero />);

    expect(screen.getByText(/your ai knowledge/i)).toBeInTheDocument();
    expect(screen.getByText(/workspace/i)).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: /start free/i })[0]).toHaveAttribute(
      "href",
      "/signup",
    );
    expect(screen.getAllByRole("link", { name: /sign in/i })[0]).toHaveAttribute(
      "href",
      "/login",
    );
  });
});
