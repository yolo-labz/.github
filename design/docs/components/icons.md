# Icons

Source: `apps/web/src/components/shared/icons.tsx` (portfolio).

## Purpose

The only icon set on the site. Authored 16 px line icons. No emoji or glyph stands in for an icon.

## Anatomy

- One `svg` shape: `viewBox 0 0 16 16`, `width` and `height` 16, `fill none`, `stroke currentColor`, `stroke-width 1.5`, round caps and joins, `aria-hidden="true"`.
- Each export passes a path string (`d`) to the shared `LineIcon`. Current exports: `ArrowRight`, `ArrowLeft`, `ArrowUpRight`. Add new ones the same way.
- Callers pass `className` only.

## Tokens used

- Colour comes from `currentColor`, so the icon takes the text colour of its parent (`text-accent`, `text-link`, `group-hover:text-accent`).
- Size is fixed by attributes (16 px). Use `className` for layout, not size.

## States

- Static. Colour and transform change come from the parent (for example `transition-transform` on hover).

## Accessibility notes

- Decorative by design: `aria-hidden="true"` on every icon. The text beside it carries the meaning.
- An icon-only control needs its own `aria-label` on the control, not on the icon.
- Contrast is that of the parent text colour. Check it against `bg` in both themes.

## Open

- Icon-only use needs a label rule. None written yet.
