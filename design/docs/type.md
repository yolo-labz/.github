# Type

Three families, by role. **Inter** sets product text (the portfolio). **Noto Serif**, with Noto Serif Display at weight 600 for
headings, sets long reading (the blog). **JetBrains Mono** sets data on both: repository names, stacks, addresses, numbers
that line up. Both sites use weights 400 and 600. The files are wired by each app; the tokens name the stack.

| Token | Value |
|---|---|
| `font.family.sans` / `serif` / `serif-display` / `mono` | the stacks above, with system fallbacks |
| `text.size.body` | `1rem`, 16px, line height 1.625 (the blog reads at 17 to 19px, line height 1.68) |
| `text.size.step-1` to `step-6` | the portfolio's fluid scale, ratio 1.125 at 360px growing to 1.2 at 1280px |
| `text.size.small` / `label` | `0.875rem` / `0.875rem` |
| `text.measure` | `50ch` in Inter, `68ch` in Noto Serif: both are about 70 characters |
| `text.tracking.display` / `heading` | `-0.025em` / `-0.02em` |

**Rules**
- Body copy is never under 16px on any width. A phone gets the same body size as a desktop, not a smaller one.
- Headings are weight 600 with tight tracking. Paragraphs use `text-wrap: pretty`.
- Tabular figures on tables and dates only. They widen punctuation in prose.
- Sizes come from a scale. A size that is not in one needs a reason in the PR.
- Mono is for data. Prose set in mono is a different surface.

**Right:** `font-size: var(--yl-text-size-step-4)` on a section heading.
**Wrong:** `font-size: 1.73rem`, a size nobody else uses, set by eye.

**Open.** The blog keeps its own reading scale (`--step--2` to `--step-5`, ratio 1.25 on a fluid 17 to 19px base) in
`00-system.css`. It is not in the tokens: moving it changes how every post reads, so it waits for a visual review.

## Tailwind names (the portfolio)

`tracking-display`, `tracking-heading`, `tracking-label`; `leading-body`, `leading-heading`, `leading-tight`; `max-w-measure`;
`text-sm` (14px) and `text-base` (16px); `rounded-sm` 4px, `rounded-md` 8px, `rounded-lg` 12px; `shadow-float`. These replace
Tailwind's own values of the same names (`leading-tight` was 1.25, `rounded-md` was 6px), so a utility means one thing in every repo.
Wrong: `tracking-[-0.025em]`, `leading-[1.1]`, `max-w-[50ch]`. Right: `tracking-display`, `leading-tight`, `max-w-measure`.
