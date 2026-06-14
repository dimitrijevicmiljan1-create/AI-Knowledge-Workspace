"use client";

import { motion } from "framer-motion";

import { pageVariants, transitionDefault } from "@/lib/motion";

export function PageTransition({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
      transition={transitionDefault}
    >
      {children}
    </motion.div>
  );
}
