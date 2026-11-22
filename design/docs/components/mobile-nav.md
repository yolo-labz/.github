# Mobile nav

Source: `apps/web/src/components/layout/mobile-nav.tsx` (portfolio). Used inside `header.tsx`.

## Purpose

Menu button and side drawer for viewports below `md`. Lists the same `navItems` as the desktop bar.

## Anatomy

- Trigger: `button` 44 × 44 px, three 2 px bars drawn with `bg-text`. Morphs to an X when open.
- Scrim: `div` fixed, `bg-crust/80`, closes on click, `aria-hidden`.
- Drawer: `nav[role="dialog"][aria-modal="true"]`, 288 px wide, `bg-bg-elevated`, `shadow-float`, `p-6`, `mt-16` list.
- Links: `min-h-11`, `px-4 py-3`, `text-lg text-text-muted`, hover `bg-surface` and `text-text`.

## Tokens used

- `bg-text` (bars), `bg-crust/80` (scrim), `bg-bg-elevated` (drawer), `bg-surface` (hover), `text-text-muted`, `text-text`, `shadow-float`, `rounded-md`.
- Motion: `duration-200` on bars; drawer entrance from `globals.css` (`.drawer-*`), off under reduced motion.

## States

- Closed, open, link hover, link focus.
- While open: body scroll locked (`overflow: hidden`), focus moves to the first link, Escape closes and returns focus to the trigger, Tab cycles inside the dialog.

## Accessibility notes

- Trigger has `aria-label` ("Open menu" / "Close menu") and `aria-expanded`.
- Dialog is modal, labelled "Navigation menu". Focus trap is in `trapFocus`.
- Scrim is `aria-hidden`; it is a click target only. Keyboard users close with Escape.
- Every link is 44 px tall.

## Open

- Trap selector includes `[tabindex]`; the trigger sits outside the dialog, so Tab leaves the drawer only through the trap. Re-check after header changes.
