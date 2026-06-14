import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { Hero } from "@/components/landing/hero";

describe("Hero", () => {
  it("renders headline and call-to-action buttons", () => {
    render(<Hero />);

    expect(screen.getByText(/your knowledge\./i)).toBeInTheDocument();
    expect(screen.getByText(/searchable\. chatable\. intelligent\./i)).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: /get started/i })[0]).toHaveAttribute(
      "href",
      "/signup",
    );
    expect(screen.getAllByRole("link", { name: /sign in/i })[0]).toHaveAttribute(
      "href",
      "/login",
    );
  });
});
