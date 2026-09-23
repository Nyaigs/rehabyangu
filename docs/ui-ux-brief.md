# RehabYangu — UI/UX Design Brief

**Version:** 0.2
**Owner:** WeiraLynk Design
**Status:** Current
**Last Updated:** 2026-09-23

## 1. Design Philosophy

RehabYangu's UI should communicate trust, professionalism, clarity, and calm. It should feel like a premium healthcare SaaS product.

Source of truth: `frontend/src/index.css` and `frontend/tailwind.config.js`.

## 2. Colour Palette

### Primary (brand green)

| Token | Value | Use |
|---|---|---|
| Primary | #17614f | Primary actions, links, active states |
| Primary dark | #104c3e | Hover states |
| Primary light | #E6F4EF | Backgrounds for tags and badges |

### Secondary (deep teal)

| Token | Value | Use |
|---|---|---|
| Secondary | #1D5A70 | Accents, secondary headings |

### Accent (warm amber)

| Token | Value | Use |
|---|---|---|
| Accent | #D97706 | Attention without alarm |

### Semantic colours

| Meaning | Background | Text |
|---|---|---|
| Success | #D1FAE5 | #065F46 |
| Warning | #FEF3C7 | #92400E |
| Danger | #FEE2E2 | #991B1B |
| Info | #DBEAFE | #1E40AF |
| Neutral | #F1F5F9 | #334155 |

### Rules
- Never rely on colour alone to convey meaning (WCAG 1.4.1).
- Use soft backgrounds for badges and banners.
- Primary buttons solid; secondary outline.

## 3. Typography

Font family: IBM Plex Sans (loaded locally via @fontsource/ibm-plex-sans, weights 400, 500, 600, 700).

| Element | Size | Weight | Line-height |
|---|---|---|---|
| Body text | 16px | 500 | 1.6 |
| Small / caption | 14px | 500 | 1.5 |
| Table cells | 15px | 500 | 1.5 |
| Section headings | 18px | 600 | 1.4 |
| Page titles | 24px | 700 | 1.3 |
| Large display | 32px | 700 | 1.25 |

Contrast:
- Primary text: #1A2B35 (15:1)
- Secondary text: #3D4F5C (7:1)
- Muted text: #64748B (4.5:1 minimum, WCAG AA)

## 4. Spacing

Consistent scale: 4px / 8px / 16px / 24px / 32px.
Page padding: 24px desktop, 16px mobile.
Card padding: 24px desktop, 16px mobile.

## 5. Components

All UI uses the shared library in frontend/src/components/ui/:

- Button (primary, secondary, danger, ghost; sizes sm / default / lg)
- Table (sortable, responsive)
- Modal (Radix-based, focus-trapped, ESC-to-close)
- Badge (semantic tones)
- FormFields (Field, SelectField, TextareaField)
- ErrorBanner, EmptyState, Skeleton

## 6. Interactions

- Page transitions: fade-in 150–200ms
- Modal open/close: fade + slight scale 150ms
- Button press: brief scale-95
- Toasts: slide-in from top-right, auto-dismiss 4s
- Skeletons: shimmer

CSS transitions only — no heavy animation libraries.

## 7. Accessibility

Target: WCAG 2.1 AA.
- Keyboard reachable
- Visible focus rings
- Modals trap focus; Escape closes
- Alt text on images
- 4.5:1 contrast minimum
- 44×44px touch targets

## 8. Breakpoints

Mobile 375px+, Tablet 768px+, Desktop 1366px+.
Sidebar becomes slide-in overlay on mobile.
