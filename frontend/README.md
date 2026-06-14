# AI Knowledge Workspace — Frontend

Next.js 15 application for the AI Knowledge Workspace SaaS platform.

## Design System

All UI must follow the global design system. See [../docs/DESIGN_SYSTEM.md](../docs/DESIGN_SYSTEM.md).

Key files:

- `src/app/globals.css` — Color tokens and theme
- `src/lib/motion.ts` — Framer Motion animation presets
- `src/components/ui/` — shadcn/ui components
- `src/components/layout/` — App shell, sidebar, header

## Stack

- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS v4
- shadcn/ui (base-nova)
- Framer Motion
- TanStack Query
- Lucide Icons

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Scripts

```bash
npm run dev      # Development server
npm run build    # Production build
npm run start    # Start production server
npm run lint     # ESLint
```
