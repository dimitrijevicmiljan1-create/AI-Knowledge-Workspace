import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { MessageBubble } from "@/components/chat/message-bubble";

describe("MessageBubble", () => {
  it("renders assistant markdown content", () => {
    render(
      <MessageBubble
        role="assistant"
        content="Here is **bold** text and `code`."
        citations={[{ id: "1", documentTitle: "Guide.md" }]}
      />,
    );

    expect(screen.getByText(/bold/i)).toBeInTheDocument();
    expect(screen.getByText("Guide.md")).toBeInTheDocument();
  });
});
