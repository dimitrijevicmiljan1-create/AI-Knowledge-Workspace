export function PricingPlaceholder() {
  return (
    <section
      id="pricing"
      className="border-t border-border px-4 py-20 sm:px-6"
      aria-labelledby="pricing-heading"
    >
      <div className="mx-auto max-w-3xl text-center">
        <h2 id="pricing-heading" className="text-section-title">
          Pricing
        </h2>
        <p className="mt-3 text-body text-text-secondary">
          Pricing plans will be announced soon. Start free today while we
          finalize tiers for teams and enterprises.
        </p>
        <p className="mt-6 text-meta">Coming soon</p>
      </div>
    </section>
  );
}

export function DocumentationPlaceholder() {
  return (
    <section
      id="documentation"
      className="border-t border-border px-4 py-20 sm:px-6"
      aria-labelledby="docs-heading"
    >
      <div className="mx-auto max-w-3xl text-center">
        <h2 id="docs-heading" className="text-section-title">
          Documentation
        </h2>
        <p className="mt-3 text-body text-text-secondary">
          Guides for connecting sources, configuring workspaces, and using RAG
          chat will be published here.
        </p>
        <p className="mt-6 text-meta">Coming soon</p>
      </div>
    </section>
  );
}
