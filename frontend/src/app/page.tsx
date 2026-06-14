import { Sparkles } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function HomePage() {
  return (
    <section className="space-y-8">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">Welcome</h2>
        <p className="max-w-2xl text-text-secondary">
          AI Knowledge Workspace is a SaaS platform for organizing and querying
          knowledge with AI. Built for speed, focus, and a premium developer
          experience.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="size-4 text-primary" />
              AI-Powered Search
            </CardTitle>
            <CardDescription>
              Query your knowledge base with natural language and get cited answers.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              RAG pipeline with streaming-ready architecture.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Knowledge Sources</CardTitle>
            <CardDescription>
              Connect documents, GitHub repos, and more into unified workspaces.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Organize sources with modern data tables and filters.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Chat Experience</CardTitle>
            <CardDescription>
              ChatGPT-inspired conversations with message grouping and auto-scroll.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Smooth transitions and typing indicator support built in.
            </p>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
