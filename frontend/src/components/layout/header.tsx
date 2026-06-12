import { Button } from "@/components/ui/button";

export function Header() {
  return (
    <header className="flex h-16 items-center justify-between border-b bg-background px-6">
      <div>
        <h1 className="text-lg font-semibold">AI Knowledge Workspace</h1>
        <p className="text-sm text-muted-foreground">
          Foundation phase — architecture and infrastructure only
        </p>
      </div>
      <div className="flex items-center gap-2">
        <Button variant="outline" size="sm">
          Placeholder
        </Button>
      </div>
    </header>
  );
}
