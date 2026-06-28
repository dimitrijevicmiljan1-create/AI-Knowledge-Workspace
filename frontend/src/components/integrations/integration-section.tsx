type IntegrationSectionProps = {
  title: string;
  emoji: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
};

export function IntegrationSection({
  title,
  emoji,
  children,
  footer,
}: IntegrationSectionProps) {
  return (
    <section className="space-y-4">
      <h2 className="text-sm font-semibold tracking-tight">
        <span aria-hidden="true" className="mr-2">
          {emoji}
        </span>
        {title}
      </h2>
      {children}
      {footer}
    </section>
  );
}
