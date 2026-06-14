"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { FolderPlus } from "lucide-react";
import { useState } from "react";

import { ApiError } from "@/lib/api/client";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useCreateWorkspace } from "@/hooks/use-workspaces";
import { formVariants, transitionDefault } from "@/lib/motion";
import { routes } from "@/lib/routes";

export function OnboardingForm() {
  const router = useRouter();
  const createWorkspace = useCreateWorkspace();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const trimmedName = name.trim();
    if (!trimmedName) {
      setError("Workspace name is required.");
      return;
    }

    try {
      await createWorkspace.mutateAsync({
        name: trimmedName,
        description: description.trim() || undefined,
      });
      router.push(routes.dashboard);
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "Unable to create workspace. Please check your connection and try again.",
        );
      }
    }
  }

  return (
    <motion.div
      initial="initial"
      animate="animate"
      variants={formVariants}
      transition={transitionDefault}
      className="space-y-6"
    >
      <div className="space-y-2 text-center">
        <div className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-primary/10">
          <FolderPlus className="size-6 text-primary" aria-hidden="true" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight">
          Create your first workspace
        </h1>
        <p className="text-sm text-text-secondary">
          Workspaces organize your sources, documents, and conversations.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Workspace details</CardTitle>
          <CardDescription>
            Choose a name for your workspace. You can update this later.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <div className="space-y-2">
              <label className="text-sm font-medium" htmlFor="workspace-name">
                Workspace Name
              </label>
              <Input
                id="workspace-name"
                type="text"
                required
                maxLength={255}
                value={name}
                onChange={(event) => setName(event.target.value)}
                disabled={createWorkspace.isPending}
              />
            </div>
            <div className="space-y-2">
              <label
                className="text-sm font-medium"
                htmlFor="workspace-description"
              >
                Description{" "}
                <span className="font-normal text-muted-foreground">
                  (optional)
                </span>
              </label>
              <Textarea
                id="workspace-description"
                rows={3}
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                disabled={createWorkspace.isPending}
              />
            </div>
            {error ? (
              <p className="text-sm text-destructive" role="alert">
                {error}
              </p>
            ) : null}
            <Button
              type="submit"
              className="w-full"
              disabled={createWorkspace.isPending}
            >
              {createWorkspace.isPending
                ? "Creating workspace..."
                : "Create Workspace"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  );
}
