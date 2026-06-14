"use client";

import { motion } from "framer-motion";

import { MarkdownContent } from "@/components/chat/markdown-content";
import {
  CitationList,
  type Citation,
} from "@/components/chat/citation-badge";
import { chatMessageVariants, transitionDefault } from "@/lib/motion";
import { cn } from "@/lib/utils";

type MessageBubbleProps = {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  className?: string;
};

export function MessageBubble({
  role,
  content,
  citations = [],
  className,
}: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <motion.div
      initial="initial"
      animate="animate"
      variants={chatMessageVariants}
      transition={transitionDefault}
      className={cn("flex w-full", isUser ? "justify-end" : "justify-start", className)}
    >
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-4 py-3 sm:max-w-[75%]",
          isUser
            ? "bg-primary text-primary-foreground"
            : "border border-border bg-elevated",
        )}
      >
        {isUser ? (
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{content}</p>
        ) : (
          <>
            <MarkdownContent content={content} />
            <CitationList citations={citations} />
          </>
        )}
      </div>
    </motion.div>
  );
}
