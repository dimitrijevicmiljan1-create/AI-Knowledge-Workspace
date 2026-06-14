import type { Metadata } from "next";

import { Cta } from "@/components/landing/cta";
import { Features } from "@/components/landing/features";
import { Footer } from "@/components/landing/footer";
import { Hero } from "@/components/landing/hero";
import { Integrations } from "@/components/landing/integrations";
import { PublicNavbar } from "@/components/layout/public-navbar";

const title = "AI Knowledge Workspace — Searchable, Chatable, Intelligent";
const description =
  "Connect GitHub repositories, Obsidian vaults and documents. Search everything instantly and chat with your knowledge using AI.";

export const metadata: Metadata = {
  title,
  description,
  openGraph: {
    title,
    description,
    type: "website",
    siteName: "AI Knowledge Workspace",
  },
  twitter: {
    card: "summary_large_image",
    title,
    description,
  },
};

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <PublicNavbar />
      <main>
        <Hero />
        <Features />
        <Integrations />
        <Cta />
      </main>
      <Footer />
    </div>
  );
}
