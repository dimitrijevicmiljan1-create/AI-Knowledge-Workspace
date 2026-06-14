"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useMemo, useState } from "react";

import { useWorkspaces, workspacesQueryKey } from "@/hooks/use-workspaces";
import {
  getActiveWorkspaceId,
  setActiveWorkspaceId,
} from "@/lib/workspace-storage";

export function useActiveWorkspace() {
  const { data: workspaces, isLoading, isError, error } = useWorkspaces();
  const [activeWorkspaceId, setActiveWorkspaceIdState] = useState<string | null>(
    null,
  );
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    if (!workspaces?.items.length) {
      setIsInitialized(true);
      return;
    }

    const storedId = getActiveWorkspaceId();
    const storedExists = storedId
      ? workspaces.items.some((workspace) => workspace.id === storedId)
      : false;

    const nextId = storedExists ? storedId : workspaces.items[0].id;
    if (nextId) {
      setActiveWorkspaceId(nextId);
      setActiveWorkspaceIdState(nextId);
    }
    setIsInitialized(true);
  }, [workspaces]);

  const activeWorkspace = useMemo(() => {
    if (!workspaces?.items.length || !activeWorkspaceId) {
      return null;
    }
    return (
      workspaces.items.find((workspace) => workspace.id === activeWorkspaceId) ??
      workspaces.items[0]
    );
  }, [activeWorkspaceId, workspaces]);

  const selectWorkspace = useCallback((workspaceId: string) => {
    setActiveWorkspaceId(workspaceId);
    setActiveWorkspaceIdState(workspaceId);
  }, []);

  return {
    workspaces: workspaces?.items ?? [],
    activeWorkspace,
    activeWorkspaceId: activeWorkspace?.id ?? null,
    isLoading: isLoading || !isInitialized,
    isError,
    error,
    selectWorkspace,
  };
}

export function useActiveWorkspaceQueryKey(baseKey: readonly string[]) {
  const { activeWorkspaceId } = useActiveWorkspace();
  return [...baseKey, activeWorkspaceId] as const;
}

export function useInvalidateWorkspaceQueries() {
  const queryClient = useQueryClient();

  return () => {
    queryClient.invalidateQueries({ queryKey: workspacesQueryKey });
  };
}
