# AI Knowledge Workspace — Global UI/UX Design System

**IMPORTANT:** This design system applies to **ALL frontend phases**. Every page, component, modal, sidebar, table, and chat interface must follow these guidelines. Do not invent new styles per page. Maintain a consistent visual language throughout the application.

Implementation lives in:

- `frontend/src/app/globals.css` — CSS tokens (single source of truth for colors, radii)
- `frontend/src/lib/motion.ts` — Framer Motion presets
- `frontend/src/components/ui/` — shadcn/ui primitives
- `frontend/src/components/layout/` — Shell, sidebar, header, page transitions

---

## Design Goal

Modern AI SaaS product.

**Visual inspiration:** ChatGPT, Linear, Vercel, Notion, Raycast, Cursor

The application should feel:

- Premium
- Fast
- Minimal
- Focused
- Modern
- Developer-friendly

**Avoid:**

- Corporate enterprise look
- Bootstrap appearance
- Generic admin dashboard appearance
- Excessive colors
- Heavy borders

---

## Color System

| Token | Hex | Usage |
|-------|-----|-------|
| Primary Background | `#0A0A0A` | `--background` |
| Secondary Background | `#111111` | `--secondary`, `--sidebar` |
| Card Background | `#18181B` | `--card` |
| Border | `#27272A` | `--border` |
| Primary Text | `#FAFAFA` | `--foreground` |
| Secondary Text | `#A1A1AA` | `--text-secondary` |
| Muted Text | `#71717A` | `--muted-foreground` |
| Accent (Purple) | `#8B5CF6` | `--primary` |
| Hover Purple | `#7C3AED` | `--primary-hover` |
| Success | `#22C55E` | `--success` |
| Warning | `#EAB308` | `--warning` |
| Error | `#EF4444` | `--error`, `--destructive` |

Use Tailwind classes mapped to tokens: `bg-background`, `text-text-secondary`, `bg-primary`, `hover:bg-primary-hover`, etc.

---

## Typography

- **Font:** Inter (`next/font/google`), fallback `system-ui`
- **Weights:** 400, 500, 600, 700
- Large headings: bold, clean spacing
- Avoid oversized typography

---

## Layout

```
Sidebar
  ↓
Header
  ↓
Content Area (max-w-7xl)
```

- Sidebar layout via `AppShell`
- Content width: `max-w-7xl` with generous whitespace
- Avoid crowded layouts

---

## Sidebar

Inspired by ChatGPT and Cursor.

- Smooth collapse/expand (200–300ms) via Framer Motion
- Icons + labels when expanded; icons only when collapsed
- Mobile: drawer with blurred backdrop
- State persisted in `localStorage`
- Use `bg-sidebar`, `border-sidebar-border`, `text-sidebar-foreground`

---

## Animations

Use **Framer Motion** (`frontend/src/lib/motion.ts`).

Required animations:

- Sidebar transitions
- Page transitions (`PageTransition`)
- Modal transitions (`modalVariants`, `backdropVariants`)
- Chat transitions (`chatMessageVariants`)
- List appearance (`listItemVariants`)
- Hover effects (CSS transitions on interactive elements)

Avoid slow, heavy, or overly playful motion. Keep animations professional.

---

## Chat Experience

Inspired by ChatGPT.

- Conversation list in sidebar (future phases)
- Smooth switching between chats
- Animated message appearance (`chatMessageVariants`)
- Streaming-ready architecture
- Message grouping, auto-scroll, typing indicator support

---

## Cards

- `rounded-2xl`
- Subtle borders (`border-border`)
- Dark surfaces (`bg-card`)
- Soft shadows with hover elevation
- Use `@/components/ui/card`

---

## Buttons

| Variant | Style |
|---------|-------|
| Primary | Purple (`bg-primary`, `hover:bg-primary-hover`) |
| Secondary | Dark (`bg-secondary`) |
| Ghost | Minimal, muted hover |

All buttons require hover transitions. Use `@/components/ui/button`.

---

## Tables

- Modern data tables — no old-style admin tables
- Row hover states
- Compact spacing
- Add via shadcn/ui when needed; follow token colors

---

## Modals

- Centered
- Blurred backdrop (`backdrop-blur-sm`, `bg-black/60`)
- Smooth open/close (`modalVariants`)
- Rounded corners
- Add shadcn Dialog when implementing modals

---

## Forms

- Clean labels
- Consistent spacing
- Inline validation
- Loading and disabled states
- Use shadcn form components when added

---

## Loading States

Use skeleton loaders (`@/components/ui/skeleton`). Avoid simple spinners whenever possible.

---

## Empty States

Use `@/components/ui/empty-state`:

- Custom icon (pass as `React.ReactNode`, e.g. `<Icon className="size-6 text-muted-foreground" />`)
- Helpful guidance text
- Clear call-to-action when applicable

---

## Mobile Experience

- Fully responsive
- Sidebar becomes drawer (`Sidebar` mobile mode)
- Chat remains usable
- No horizontal scrolling (`overflow-x-hidden` on main)

---

## Component Library

| Tool | Purpose |
|------|---------|
| shadcn/ui | Component primitives |
| Tailwind CSS v4 | Styling |
| Framer Motion | Animations |
| Lucide Icons | Icons |
| TanStack Query | Server state (`AppProviders`) |

---

## Consistency Rule

Every future frontend phase must reuse:

- Colors from `globals.css`
- Typography (Inter)
- Spacing patterns (`max-w-7xl`, `space-y-*`, `p-4 sm:p-6`)
- Sidebar and layout shell
- Animation patterns from `lib/motion.ts`

**No page-specific design systems allowed.** This document and `globals.css` are the single source of truth.

---

## Production Application Rules

This is a **production SaaS application** for real users.

**Do NOT create:** mock data, fake repositories, fake workspaces, placeholder documents, demo conversations, or sample statistics.

**Required:**

- All UI consumes real backend APIs (`frontend/src/lib/api/`)
- TanStack Query for server state
- Proper empty states when data is unavailable
- Error states when API requests fail — never fall back to fabricated content

See `.cursor/rules/production-application.mdc` for full rules.

---

## Adding New UI

1. Check if a shadcn component exists — add via CLI if not
2. Use design tokens, never hardcoded hex in components
3. Reuse `Card`, `Button`, `Skeleton`, `EmptyState`
4. Wrap new routes in existing `AppShell` layout
5. Use motion presets from `lib/motion.ts` for animations
