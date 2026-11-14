# Spacing, radius, motion, breakpoints

**Spacing** is a 4px base: `space.1` 4, `2` 8, `3` 12, `4` 16, `6` 24, `8` 32, `12` 48, `18` 72, `28` 112 (the blog names the same steps `3xs` to `3xl`).
Row gap 8, group gap 24, section gap 112.

**Radius:** `none` 0, `sm` 4px (buttons, focus ring, inline code), `md` 8px (blocks, figures), `lg` 12px (a container that has to be a container). Round things are `50%`.

**Shadow:** none by default. Depth comes from 1px rules and one tonal band. Only a floating layer (menu, popover, a lifted figure) may cast one.

**Motion:** `fast` 160ms, `base` 200ms, `medium` 300ms, `slow` 520ms. `ease.out-expo`, `cubic-bezier(0.16, 1, 0.3, 1)`, is the one curve both sites already use; `ease.standard` is for the rare symmetric move.
Animate transform and clip-path, never layout. Under `prefers-reduced-motion: reduce` the animation is not applied at all.

**Breakpoints:** `sm` 640, `md` 768, `lg` 1024, `xl` 1280. Write mobile first and add `min-width` queries.

**On a phone** (the tokens `viewport.floor`, `touch.*`, `text.min-body`)
- Nothing overflows horizontally at 360px.
- A target is 44px high and wide at least, and 8px from the next one. Size or padding makes the target, not the gap around it.
- Gutter is at least 16px under `md` and 24px from `md` up. The blog's fluid 18 to 40px clears both.
- Body is 16px. Step sizes already shrink with the viewport.

**Right:** a nav link with `min-height: var(--yl-touch-min)` and `padding-inline: var(--yl-space-2)`.
**Wrong:** a 17px-tall link that passes only because of the WCAG spacing exception (portfolio#176 measured four of those).

**Right:** `@media (min-width: 768px)`.
**Wrong:** `@media (max-width: 68rem)`. 1088px is not a breakpoint here; the blog has that one and `44rem` (704px) to migrate. Its `40rem` is `sm`.
