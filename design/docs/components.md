# Components and page rules

These rules each settled a real argument on the portfolio and the blog. Add one only with the argument it settled
and a failing example. A rule with no failing example is decoration.

1. **An index is a register, not an essay.** One lede sentence, then the entries.
   Right: the portfolio work index, first entry above the fold. Wrong: three paragraphs of positioning above the list, first entry at 735px on an 844px phone (blog#196).
2. **No cards.** Depth is 1px rules and one tonal band.
   Right: hairline rows. Wrong: a filled, inset, rounded block around one entry.
3. **One wayfinding device:** the mauve node on a quiet rail, never a node without its rail.
4. **Register meta is one line,** separators trailing, never crossing the rail. Wrong: a line that starts with a dot.
5. **The share surface is one artefact.** The image the site serves is the image the policy declares, byte for byte, at a URL that resolves.
6. **Every page family ships the large card,** its alt text, a canonical URL and hreflang.
7. **Targets are 44px,** on a phone and on a desktop. See spacing.
8. **Brand art comes from the published brand files,** never from type. Wrong: a share card drawn in code (portfolio#184).
9. **A quality claim needs a sample,** a distribution and a bound. Wrong: "fixed" after six clean loads.

**Primary action:** emerald fill, `accent.on` text, `radius.sm`. In the header only; elsewhere the action is an underlined link.
**Focus:** a 2px ring in `focus.ring`, 3px offset, on every focusable element. Never `outline: none` without a replacement.
**Icons:** 16px line arrows, 1.5 stroke, round caps, `currentColor`. No text glyph stands in for an icon.

Which document decides: page claims and org positioning, `docs/brand-positioning.md`; tokens and these rules, this folder;
what a site's file says about itself, that site's `DESIGN.md`.
