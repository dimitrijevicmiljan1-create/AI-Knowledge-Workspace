import { HomeContent } from "@/components/home/home-content";

export default function HomePage() {
  return (
    <section className="space-y-8">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">Welcome</h2>
        <p className="max-w-2xl text-text-secondary">
          AI Knowledge Workspace helps you organize, search, and query your
          knowledge with AI.
        </p>
      </div>

      <HomeContent />
    </section>
  );
}
