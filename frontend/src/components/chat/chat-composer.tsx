"use client";

import { Send } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

type ChatComposerProps = {
  onSubmit?: (message: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
  placeholder?: string;
};

export function ChatComposer({
  onSubmit,
  disabled = false,
  isLoading = false,
  placeholder = "Ask a question about your knowledge…",
}: ChatComposerProps) {
  const [value, setValue] = useState("");

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled || isLoading) return;
    onSubmit?.(trimmed);
    setValue("");
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-border bg-background/80 p-3 backdrop-blur-md sm:p-4"
    >
      <div className="mx-auto flex max-w-3xl items-end gap-2">
        <Textarea
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder={placeholder}
          disabled={disabled || isLoading}
          rows={1}
          className="min-h-[44px] max-h-32 resize-none bg-surface"
          aria-label="Chat message"
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              handleSubmit(event);
            }
          }}
        />
        <Button
          type="submit"
          size="icon"
          disabled={disabled || isLoading || !value.trim()}
          aria-label="Send message"
        >
          <Send className="size-4" />
        </Button>
      </div>
    </form>
  );
}
