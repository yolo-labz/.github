# Type

Two families. Inter for text, JetBrains Mono for data: repository names, stacks, addresses, numbers that line up.
The files are wired by each app (Next injects a hashed Inter with fallback metrics); the tokens name the stack.

| Token | Value |
|---|---|
| `text.size.body` | `1rem`, 16px, line height 1.625 |
| `text.size.step-1` to `step-6` | fluid scale, ratio 1.125 at 360px growing to 1.2 at 1280px |
| `text.size.small` / `label` | `0.875rem` / `0.75rem` |
| `text.measure` | `50ch`, about 70 characters in Inter |
| `text.tracking.display` / `heading` | `-0.025em` / `-0.02em` |

**Rules**
- Body copy is never under 16px on any width. A phone gets the same body size as a desktop, not a smaller one.
- Headings are weight 600, tight tracking, `text-wrap: balance`. Paragraphs use `text-wrap: pretty`.
- Tabular figures on tables and dates only. They widen punctuation in prose.
- Sizes come from the scale. A size that is not in it needs a reason in the PR.

**Right:** `font-size: var(--yl-text-size-step-4)` on a section heading.
**Wrong:** `font-size: 1.73rem`, a size nobody else uses, set by eye.

**Known gap.** The blog still sets its body in IBM Plex Mono at 18px and its headings in IBM Plex Sans. That is a
decision about how every post reads, so it is Pedro's, not a find-and-replace. Until then the blog is the one listed exception.
