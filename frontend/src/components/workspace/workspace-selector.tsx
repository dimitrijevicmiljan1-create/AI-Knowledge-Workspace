"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Check, ChevronDown, Plus } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useActiveWorkspace } from "@/hooks/use-active-workspace";
import { useCreateWorkspace } from "@/hooks/use-workspaces";
import { dropdownVariants, transitionFast } from "@/lib/motion";
import { cn } from "@/lib/utils";
import type { Workspace } from "@/lib/api/types";

type WorkspaceSelectorProps = {
  className?: string;
};

export function WorkspaceSelector({ className }: WorkspaceSelectorProps) {
  const {
    workspaces,
    activeWorkspace,
    isLoading,
    selectWorkspace,
  } = useActiveWorkspace();
  const createWorkspace = useCreateWorkspace();
  const [open, setOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [newWorkspaceName, setNewWorkspaceName] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
        setIsCreating(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function handleCreateWorkspace(event: React.FormEvent) {
    event.preventDefault();
    const trimmed = newWorkspaceName.trim();
    if (!trimmed) {
      return;
    }
    const workspace = await createWorkspace.mutateAsync({ name: trimmed });
    selectWorkspace(workspace.id);
    setNewWorkspaceName("");
    setIsCreating(false);
    setOpen(false);
  }

  if (isLoading) {
    return <Skeleton className={cn("h-8 w-36", className)} />;
  }

  if (!activeWorkspace) {
    return (
      <span className={cn("text-sm font-medium text-text-secondary", className)}>
        No workspace
      </span>
    );
  }

  return (
    <div className={cn("relative", className)} ref={containerRef}>
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex max-w-[200px] items-center gap-1.5 rounded-lg border border-border bg-surface px-2.5 py-1.5 text-sm font-medium transition-colors hover:bg-elevated sm:max-w-xs"
        aria-label="Select workspace"
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        <span className="truncate">{activeWorkspace.name}</span>
        <ChevronDown className="size-3.5 shrink-0 text-text-secondary" />
      </button>

      <AnimatePresence>
        {open ? (
          <motion.div
            initial="initial"
            animate="animate"
            exit="exit"
            variants={dropdownVariants}
            transition={transitionFast}
            className="absolute left-0 top-full z-50 mt-2 w-72 overflow-hidden rounded-xl border border-border bg-elevated py-1 shadow-xl"
            role="listbox"
            aria-label="Workspaces"
          >
            <div className="max-h-64 overflow-y-auto py-1">
              {workspaces.map((workspace: Workspace) => (
                <button
                  key={workspace.id}
                  type="button"
                  role="option"
                  aria-selected={workspace.id === activeWorkspace.id}
                  className="flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-sm hover:bg-accent"
                  onClick={() => {
                    selectWorkspace(workspace.id);
                    setOpen(false);
                  }}
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium">{workspace.name}</p>
                    <p className="text-meta">
                      Created {new Date(workspace.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  {workspace.id === activeWorkspace.id ? (
                    <Check className="size-4 shrink-0 text-primary" />
                  ) : null}
                </button>
              ))}
            </div>

            <div className="border-t border-border p-2">
              {isCreating ? (
                <form onSubmit={handleCreateWorkspace} className="space-y-2">
                  <input
                    value={newWorkspaceName}
                    onChange={(event) => setNewWorkspaceName(event.target.value)}
                    placeholder="Workspace name"
                    className="h-9 w-full rounded-lg border border-border bg-surface px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    aria-label="New workspace name"
                    autoFocus
                  />
                  <div className="flex gap-2">
                    <Button
                      type="submit"
                      size="sm"
                      className="flex-1"
                      disabled={createWorkspace.isPending}
                    >
                      Create
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      onClick={() => setIsCreating(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              ) : (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => setIsCreating(true)}
                >
                  <Plus className="size-4" />
                  Create workspace
                </Button>
              )}
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
}
