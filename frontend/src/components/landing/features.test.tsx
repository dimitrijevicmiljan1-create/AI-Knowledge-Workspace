import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { Features } from "@/components/landing/features";

describe("Features", () => {
  it("renders feature cards", () => {
    render(<Features />);

    expect(screen.getByRole("heading", { name: /everything you need/i })).toBeInTheDocument();
    expect(screen.getByText(/github integration/i)).toBeInTheDocument();
    expect(screen.getByText(/ai chat/i)).toBeInTheDocument();
    expect(screen.getByText(/semantic search/i)).toBeInTheDocument();
  });
});
