# Spacing, radius, motion, breakpoints

**Spacing** is a 4px base: `space.1` 4, `2` 8, `3` 12, `4` 16, `6` 24, `8` 32, `12` 48, `16` 64, `28` 112.
Row gap 8, group gap 24, section gap 112.

**Radius:** `none` 0, `sm` 2px (buttons, focus ring), `md` 6px (inline code, blog blocks), `lg` 12px (a container that has to be a container).

**Shadow:** none. Depth comes from 1px rules and one tonal band. Only a floating layer (menu, popover) may cast a shadow.

**Motion:** `fast` 150ms, `base` 200ms, `medium` 300ms, `slow` 520ms; `ease.out-expo` for entrances, `ease.standard` otherwise.
Animate transform and clip-path, never layout. Under `prefers-reduced-motion: reduce` the animation is not applied at all.

**Breakpoints:** `sm` 640, `md` 768, `lg` 1024, `xl` 1280. Write mobile first and add `min-width` queries.

**On a phone** (the tokens `viewport.floor`, `touch.*`, `text.min-body`)
- Nothing overflows horizontally at 360px.
- A target is 44px high and wide at least, and 8px from the next one. Size or padding makes the target, not the gap around it.
- Gutter is 16px under `md`, 24px from `md` up.
- Body is 16px. Step sizes already shrink with the viewport.

**Right:** a nav link with `min-height: var(--yl-touch-min)` and `padding-inline: var(--yl-space-2)`.
**Wrong:** a 17px-tall link that passes only because of the WCAG spacing exception (portfolio#176 measured four of those).

**Right:** `@media (min-width: 768px)`.
**Wrong:** `@media (max-width: 920px)`. 920 is not a breakpoint here; the blog has three of these (920, 1100, 1600) to migrate.
