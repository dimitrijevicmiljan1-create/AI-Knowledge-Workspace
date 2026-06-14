"use client";

import { motion } from "framer-motion";

export function TypingIndicator() {
  return (
    <div
      className="inline-flex items-center gap-1 rounded-2xl border border-border bg-elevated px-4 py-3"
      role="status"
      aria-label="Assistant is typing"
    >
      {[0, 1, 2].map((index) => (
        <motion.span
          key={index}
          className="size-1.5 rounded-full bg-text-secondary"
          animate={{ opacity: [0.35, 1, 0.35], y: [0, -3, 0] }}
          transition={{
            duration: 0.9,
            repeat: Infinity,
            delay: index * 0.15,
          }}
        />
      ))}
    </div>
  );
}
