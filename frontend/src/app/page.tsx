import type { Metadata } from "next";

import { Features } from "@/components/landing/features";
import { Hero } from "@/components/landing/hero";
import { LandingFooter } from "@/components/landing/landing-footer";
import {
  DocumentationPlaceholder,
  PricingPlaceholder,
} from "@/components/landing/placeholders";
import { ProductPreview } from "@/components/landing/product-preview";
import { PublicNavbar } from "@/components/layout/public-navbar";

const title = "Your AI Knowledge Workspace";
const description =
  "Connect documents, GitHub repositories and Obsidian vaults. Ask questions. Get answers with citations.";

export const metadata: Metadata = {
  title,
  description,
  openGraph: { title, description, type: "website", siteName: "AI Knowledge Workspace" },
  twitter: { card: "summary_large_image", title, description },
};

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <PublicNavbar />
      <main>
        <Hero />
        <ProductPreview />
        <Features />
        <PricingPlaceholder />
        <DocumentationPlaceholder />
      </main>
      <LandingFooter />
    </div>
  );
}
