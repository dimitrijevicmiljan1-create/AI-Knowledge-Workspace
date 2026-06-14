# AI Knowledge Workspace — Frontend

Next.js 15 application for the AI Knowledge Workspace SaaS platform.

## Design System

All UI must follow the global design system. See [../docs/DESIGN_SYSTEM.md](../docs/DESIGN_SYSTEM.md).

## Production Rules

This is a production SaaS application. **Do not use mock or placeholder data.**

- All UI must consume real backend APIs via `src/lib/api/`
- Show empty states when data is unavailable
- Never generate artificial content

See [../docs/DESIGN_SYSTEM.md](../docs/DESIGN_SYSTEM.md#production-application-rules) and `.cursor/rules/production-application.mdc`.

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
