import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { Features } from "@/components/landing/features";

describe("Features", () => {
  it("renders feature cards", () => {
    render(<Features />);

    expect(
      screen.getByRole("heading", { name: /built for knowledge work/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/knowledge sources/i)).toBeInTheDocument();
    expect(screen.getByText(/rag chat/i)).toBeInTheDocument();
    expect(screen.getByText(/citations/i)).toBeInTheDocument();
  });
});
