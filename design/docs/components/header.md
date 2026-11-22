# Header

Source: `apps/web/src/components/layout/header.tsx` (portfolio).

## Purpose

Fixed top bar on every page. Gives the home link, the section links, the locale switch and the email CTA. Below `md` it hands off to the mobile drawer (`mobile-nav.md`).

## Anatomy

- `header` (fixed, full width, `border-b`, `bg`) > `nav[aria-label="Main navigation"]` (height 56 px, max width 6xl).
- Left: home link, mono, `text-sm font-medium`.
- Right, `md` and up only: `ul` of section links, the locale switcher, and the primary CTA (`mailto:`, emerald fill).
- Right, below `md`: the mobile trigger (`MobileNav`).

## Tokens used

- Surfaces: `bg-bg`, `border-border`.
- Text: `text-text` (home, hover), `text-text-muted` (links), `text-accent` (home hover).
- CTA: `bg-accent`, `hover:bg-accent-hover`, `text-bg`, `rounded-sm` (4 px).
- Motion: `transition-colors`.
- Hit area: `min-h-11` (44 px) on every link.

## States

- Default, hover (text to `text`), focus (browser focus ring from `--yl-color-focus-ring`).
- Active page: `aria-current` is not set in this file. Gap, see Open.

## Accessibility notes

- Landmark: `nav` with a label. Desktop links are in a `ul`.
- Every link and the CTA are 44 px tall. Decision 16 (round 3): 44 px for coarse pointers, at least 24 px for fine pointers. The code uses 44 px for both today.
- In-page anchors off home go to `/#anchor` (default locale). Keep that behaviour.

## Open

- No `aria-current` on the active section link.
- Fine-pointer 24 px target not yet implemented.
